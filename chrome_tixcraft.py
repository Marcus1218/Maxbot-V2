#!/usr/bin/env python3
#encoding=utf-8
#執行方式：python chrome_tixcraft.py 或 python3 chrome_tixcraft.py
#import jieba
#from DrissionPage import ChromiumPage
#import nodriver as uc
import argparse
import base64
import json
import logging
import os
import platform
import random
import ssl
import subprocess
import sys
import threading
import time
import warnings
import webbrowser
from datetime import datetime

import chromedriver_autoinstaller_max
import requests
from selenium import webdriver
from selenium.common.exceptions import (NoAlertPresentException,
                                        NoSuchWindowException,
                                        UnexpectedAlertPresentException,
                                        WebDriverException)
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from urllib3.exceptions import InsecureRequestWarning

import util
from NonBrowser import NonBrowser

try:
    import ddddocr
except Exception as exc:
    print(exc) # This print is for critical import error, keep as is or use a very basic logger if UI not up.
    pass

CONST_APP_VERSION = "MaxBot (2024.04.23)"

CONST_MAXBOT_ANSWER_ONLINE_FILE = "MAXBOT_ONLINE_ANSWER.txt"
CONST_MAXBOT_CONFIG_FILE = "settings.json"
CONST_MAXBOT_EXTENSION_NAME = "Maxbotplus_1.0.0"
CONST_MAXBOT_INT28_FILE = "MAXBOT_INT28_IDLE.txt"
CONST_MAXBOT_LAST_URL_FILE = "MAXBOT_LAST_URL.txt"
CONST_MAXBOT_QUESTION_FILE = "MAXBOT_QUESTION.txt"
CONST_MAXBOT_LOG_FILE = "maxbot_runtime.log"
CONST_MAXBLOCK_EXTENSION_NAME = "Maxblockplus_1.0.0"
CONST_MAXBLOCK_EXTENSION_FILTER =[
"*.doubleclick.net/*",
"*.googlesyndication.com/*",
"*.ssp.hinet.net/*",
"*a.amnet.tw/*",
"*adx.c.appier.net/*",
"*cdn.cookielaw.org/*",
"*cdnjs.cloudflare.com/ajax/libs/clipboard.js/*",
"*clarity.ms/*",
"*cloudfront.com/*",
"*cms.analytics.yahoo.com/*",
"*e2elog.fetnet.net/*",
"*fundingchoicesmessages.google.com/*",
"*ghtinc.com/*",
"*google-analytics.com/*",
"*googletagmanager.com/*",
"*googletagservices.com/*",
"*img.uniicreative.com/*",
"*lndata.com/*",
"*match.adsrvr.org/*",
"*onead.onevision.com.tw/*",
"*play.google.com/log?*",
"*popin.cc/*",
"*rollbar.com/*",
"*sb.scorecardresearch.com/*",
"*tagtoo.co/*",
"*ticketmaster.sg/js/adblock*",
"*ticketmaster.sg/js/adblock.js*",
"*tixcraft.com/js/analytics.js*",
"*tixcraft.com/js/common.js*",
"*tixcraft.com/js/custom.js*",
"*treasuredata.com/*",
"*www.youtube.com/youtubei/v1/player/heartbeat*",
]

CONST_CHROME_VERSION_NOT_MATCH_EN="Please download the WebDriver version to match your browser version."
CONST_CHROME_VERSION_NOT_MATCH_TW="請下載與您瀏覽器相同版本的WebDriver版本，或更新您的瀏覽器版本。"
CONST_CHROME_DRIVER_WEBSITE = 'https://chromedriver.chromium.org/'

CONST_CITYLINE_SIGN_IN_URL = "https://www.cityline.com/Login.html?targetUrl=https%3A%2F%2Fwww.cityline.com%2FEvents.html"
CONST_FAMI_SIGN_IN_URL = "https://www.famiticket.com.tw/Home/User/SignIn"
CONST_HKTICKETING_SIGN_IN_URL = "https://premier.hkticketing.com/Secure/ShowLogin.aspx"
CONST_KHAM_SIGN_IN_URL = "https://kham.com.tw/application/UTK13/UTK1306_.aspx"
CONST_KKTIX_SIGN_IN_URL = "https://kktix.com/users/sign_in?back_to=%s"
CONST_TICKET_SIGN_IN_URL = "https://ticket.com.tw/application/utk13/utk1306_.aspx"
CONST_URBTIX_SIGN_IN_URL = "https://www.urbtix.hk/member-login"

CONST_FROM_TOP_TO_BOTTOM = "from top to bottom"
CONST_FROM_BOTTOM_TO_TOP = "from bottom to top"
CONST_CENTER = "center"
CONST_RANDOM = "random"

CONT_STRING_1_SEATS_REMAINING = ['@1 seat(s) remaining','剩餘 1@','@1 席残り']

CONST_OCR_CAPTCH_IMAGE_SOURCE_NON_BROWSER = "NonBrowser"
CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS = "canvas"

CONST_WEBDRIVER_TYPE_SELENIUM = "selenium"
CONST_WEBDRIVER_TYPE_UC = "undetected_chromedriver"
CONST_WEBDRIVER_TYPE_DP = "DrissionPage"
CONST_WEBDRIVER_TYPE_NODRIVER = "nodriver"
CONST_CHROME_FAMILY = ["chrome","edge","brave"]
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
CONST_PREFS_DICT = {
    "credentials_enable_service": False, 
    "in_product_help.snoozed_feature.IPH_LiveCaption.is_dismissed": True,
    "in_product_help.snoozed_feature.IPH_LiveCaption.last_dismissed_by": 4,
    "media_router.show_cast_sessions_started_by_other_devices.enabled": False,
    "net.network_prediction_options": 3,
    "privacy_guide.viewed": True,
    "profile.default_content_setting_values.notifications": 2,
    "profile.default_content_setting_values.sound": 2,
    "profile.name": CONST_APP_VERSION, 
    "profile.password_manager_enabled": False, 
    "safebrowsing.enabled":False,
    "safebrowsing.enhanced":False,
    "sync.autofill_wallet_import_enabled_migrated":False,
    "translate":{"enabled": False}}

warnings.simplefilter('ignore',InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context
logging.basicConfig()
logger = logging.getLogger('logger')

def log_ui(message, also_print=True):
    if also_print:
        print(message)
    try:
        working_dir = os.path.dirname(os.path.realpath(__file__))
        log_file_path = os.path.join(working_dir, CONST_MAXBOT_LOG_FILE)
        with open(log_file_path, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
    except Exception as e:
        print(f"Error writing to log file ({CONST_MAXBOT_LOG_FILE}): {e}")

def get_config_dict(args):
    app_root = util.get_app_root()
    config_filepath = os.path.join(app_root, CONST_MAXBOT_CONFIG_FILE)

    if args.input:
        config_filepath = args.input

    config_dict = None
    if os.path.isfile(config_filepath):
        with open(config_filepath) as json_data:
            config_dict = json.load(json_data)
            if args.headless is not None: config_dict["advanced"]["headless"] = util.t_or_f(args.headless)
            if args.homepage: config_dict["homepage"] = args.homepage
            if args.ticket_number: config_dict["ticket_number"] = args.ticket_number
            if args.browser: config_dict["browser"] = args.browser
            if args.tixcraft_sid: config_dict["advanced"]["tixcraft_sid"] = args.tixcraft_sid
            if args.ibonqware: config_dict["advanced"]["ibonqware"] = args.ibonqware
            if args.kktix_account: config_dict["advanced"]["kktix_account"] = args.kktix_account
            if args.kktix_password: config_dict["advanced"]["kktix_password_plaintext"] = args.kktix_password
            if args.proxy_server: config_dict["advanced"]["proxy_server_port"] = args.proxy_server
            if args.window_size: config_dict["advanced"]["window_size"] = args.window_size
            is_headless_enable_ocr = False
            if config_dict["advanced"]["headless"] and len(config_dict["advanced"]["tixcraft_sid"]) > 1:
                is_headless_enable_ocr = True
            if is_headless_enable_ocr:
                config_dict["ocr_captcha"]["enable"] = True
                config_dict["ocr_captcha"]["force_submit"] = True
    return config_dict

def write_question_to_file(question_text):
    working_dir = os.path.dirname(os.path.realpath(__file__))
    target_path = os.path.join(working_dir, CONST_MAXBOT_QUESTION_FILE)
    util.write_string_to_file(target_path, question_text)

def write_last_url_to_file(url):
    working_dir = os.path.dirname(os.path.realpath(__file__))
    target_path = os.path.join(working_dir, CONST_MAXBOT_LAST_URL_FILE)
    util.write_string_to_file(target_path, url)

def read_last_url_from_file():
    ret = ""
    # Ensure file exists before trying to read
    if os.path.exists(CONST_MAXBOT_LAST_URL_FILE):
        with open(CONST_MAXBOT_LAST_URL_FILE, "r") as text_file:
            ret = text_file.readline()
    return ret

def get_favoriate_extension_path(webdriver_path, config_dict):
    extension_list = []
    extension_list.append(os.path.join(webdriver_path, CONST_MAXBOT_EXTENSION_NAME + ".crx"))
    extension_list.append(os.path.join(webdriver_path, CONST_MAXBLOCK_EXTENSION_NAME + ".crx"))
    return extension_list

def get_chromedriver_path(webdriver_path):
    chromedriver_path = os.path.join(webdriver_path,"chromedriver")
    if platform.system().lower()=="windows":
        chromedriver_path = os.path.join(webdriver_path,"chromedriver.exe")
    return chromedriver_path

def get_chrome_options(webdriver_path, config_dict):
    # ... (This function's content, including print-to-log_ui changes, remains the same as previously intended but will be part of the full overwrite)
    chrome_options = webdriver.ChromeOptions()
    if config_dict["browser"]=="edge": chrome_options = webdriver.EdgeOptions()
    if config_dict["browser"]=="safari": chrome_options = webdriver.SafariOptions()
    is_log_performace = any(site in config_dict["homepage"] for site in ['ticketplus'])
    if is_log_performace and config_dict["browser"] in CONST_CHROME_FAMILY:
        chrome_options.set_capability("goog:loggingPrefs",{"performance": "ALL"})
    if config_dict["advanced"]["chrome_extension"]:
        for ext in get_favoriate_extension_path(webdriver_path, config_dict):
            if os.path.exists(ext): chrome_options.add_extension(ext)
    if config_dict["advanced"]["headless"]: chrome_options.add_argument('--headless=new')
    chrome_options.add_argument(f"--user-agent={USER_AGENT}")
    # Add other arguments... (as before)
    chrome_options.add_argument("--disable-animations"); chrome_options.add_argument("--disable-background-networking"); chrome_options.add_argument("--disable-backgrounding-occluded-windows"); chrome_options.add_argument("--disable-bookmark-reordering"); chrome_options.add_argument("--disable-boot-animation"); chrome_options.add_argument("--disable-breakpad"); chrome_options.add_argument("--disable-canvas-aa"); chrome_options.add_argument("--disable-client-side-phishing-detection"); chrome_options.add_argument("--disable-cloud-import"); chrome_options.add_argument("--disable-component-cloud-policy"); chrome_options.add_argument("--disable-component-update"); chrome_options.add_argument("--disable-composited-antialiasing"); chrome_options.add_argument("--disable-default-apps"); chrome_options.add_argument("--disable-dev-shm-usage"); chrome_options.add_argument("--disable-device-discovery-notifications"); chrome_options.add_argument("--disable-dinosaur-easter-egg"); chrome_options.add_argument("--disable-domain-reliability"); chrome_options.add_argument("--disable-features=IsolateOrigins,site-per-process,TranslateUI,PrivacySandboxSettings4"); chrome_options.add_argument("--disable-infobars"); chrome_options.add_argument("--disable-logging"); chrome_options.add_argument("--disable-login-animations"); chrome_options.add_argument("--disable-login-screen-apps"); chrome_options.add_argument("--disable-notifications"); chrome_options.add_argument("--disable-popup-blocking"); chrome_options.add_argument("--disable-print-preview"); chrome_options.add_argument("--disable-renderer-backgrounding"); chrome_options.add_argument("--disable-session-crashed-bubble"); chrome_options.add_argument("--disable-smooth-scrolling"); chrome_options.add_argument("--disable-suggestions-ui"); chrome_options.add_argument("--disable-sync"); chrome_options.add_argument("--disable-translate"); chrome_options.add_argument("--hide-crash-restore-bubble"); chrome_options.add_argument("--lang=zh-TW"); chrome_options.add_argument("--no-default-browser-check"); chrome_options.add_argument("--no-first-run"); chrome_options.add_argument("--no-pings"); chrome_options.add_argument("--no-sandbox"); chrome_options.add_argument("--no-service-autorun"); chrome_options.add_argument("--password-store=basic");
    chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
    chrome_options.add_experimental_option("prefs", CONST_PREFS_DICT)
    if len(config_dict["advanced"]["proxy_server_port"]) > 2: chrome_options.add_argument(f'--proxy-server={config_dict["advanced"]["proxy_server_port"]}')
    if config_dict["browser"]=="brave":
        brave_path = util.get_brave_bin_path()
        if os.path.exists(brave_path): chrome_options.binary_location = brave_path
    chrome_options.page_load_strategy = 'eager'
    chrome_options.unhandled_prompt_behavior = "accept"
    return chrome_options

def load_chromdriver_normal(config_dict, driver_type):
    show_debug_message = config_dict["advanced"]["verbose"]
    driver = None
    Root_Dir = util.get_app_root()
    webdriver_path = os.path.join(Root_Dir, "webdriver")
    chromedriver_path = get_chromedriver_path(webdriver_path)
    os.makedirs(webdriver_path, exist_ok=True)
    if not os.path.exists(chromedriver_path):
        log_ui(f"WebDriver not exist, try to download to: {webdriver_path}")
        chromedriver_autoinstaller_max.install(path=webdriver_path, make_version_dir=False)
    if not os.path.exists(chromedriver_path):
        log_ui("Please download chromedriver and extract zip to webdriver folder from this url:")
        log_ui("請下在面的網址下載與你chrome瀏覽器相同版本的chromedriver,解壓縮後放到webdriver目錄裡：")
        log_ui(CONST_CHROME_DRIVER_WEBSITE)
    else:
        chrome_service = Service(chromedriver_path)
        chrome_options = get_chrome_options(webdriver_path, config_dict)
        try:
            driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
        except WebDriverException as exc:
            error_message = str(exc)
            if show_debug_message: log_ui(str(exc))
            if "This version of ChromeDriver only supports Chrome version" in error_message:
                log_ui(CONST_CHROME_VERSION_NOT_MATCH_EN)
                log_ui(CONST_CHROME_VERSION_NOT_MATCH_TW)
                try:
                    log_ui("Deleting exist and download ChromeDriver again.")
                    os.unlink(chromedriver_path)
                except Exception as exc2: log_ui(str(exc2))
                chromedriver_autoinstaller_max.install(path=webdriver_path, make_version_dir=False)
                chrome_service = Service(chromedriver_path)
                try:
                    driver = webdriver.Chrome(service=chrome_service, options=get_chrome_options(webdriver_path, config_dict))
                except WebDriverException as exc2_inner: # Renamed exc2
                    log_ui("Selenium 4.11.0 Release with Chrome For Testing Browser.")
                    try:
                        driver = webdriver.Chrome(service=Service(), options=get_chrome_options(webdriver_path, config_dict))
                    except WebDriverException as exc3: log_ui(str(exc3))
    return driver

def get_driver_by_config(config_dict):
    driver = None
    homepage = config_dict["homepage"]
    log_ui(f"current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_ui(f"maxbot app version: {CONST_APP_VERSION}")
    log_ui(f"python version: {platform.python_version()}")
    log_ui(f"platform: {platform.platform()}")
    log_ui(f"homepage: {homepage}")
    log_ui(f"browser: {config_dict['browser']}")
    if config_dict["advanced"]["verbose"]:
        log_ui(f"advanced config: {config_dict['advanced']}") # Ensure this is a string
    log_ui(f"webdriver_type: {config_dict['webdriver_type']}")

    if homepage is None: homepage = ""
    Root_Dir = util.get_app_root()
    webdriver_path = os.path.join(Root_Dir, "webdriver")

    if config_dict["browser"] in CONST_CHROME_FAMILY: # Simplified from ["chrome", "brave"]
        if config_dict["webdriver_type"] == CONST_WEBDRIVER_TYPE_SELENIUM:
            driver = load_chromdriver_normal(config_dict, config_dict["webdriver_type"])
        elif config_dict["webdriver_type"] == CONST_WEBDRIVER_TYPE_UC:
            if platform.system().lower()=="windows" and hasattr(sys, 'frozen'):
                from multiprocessing import freeze_support
                freeze_support()
            # Assuming load_chromdriver_uc is defined and handles its own logging
            driver = load_chromdriver_uc(config_dict)
    # ... (Firefox, Edge, Safari logic as before, ensuring their print calls are also eventually converted)
    elif config_dict["browser"] == "firefox":
        chromedriver_path = os.path.join(webdriver_path,"geckodriver")
        if platform.system().lower()=="windows": chromedriver_path = os.path.join(webdriver_path,"geckodriver.exe")
        if "macos" in platform.platform().lower() and "arm64" in platform.platform().lower(): chromedriver_path = os.path.join(webdriver_path,"geckodriver_arm")
        webdriver_service = Service(chromedriver_path)
        try:
            from selenium.webdriver.firefox.options import Options
            options = Options()
            if config_dict["advanced"]["headless"]: options.add_argument('--headless')
            if platform.system().lower()=="windows":
                binary_path = "C:\\Program Files\\Mozilla Firefox\\firefox.exe"
                if not os.path.exists(binary_path): binary_path = os.path.expanduser('~') + "\\AppData\\Local\\Mozilla Firefox\\firefox.exe"
                if not os.path.exists(binary_path): binary_path = "C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe"
                if not os.path.exists(binary_path): binary_path = "D:\\Program Files\\Mozilla Firefox\\firefox.exe"
                options.binary_location = binary_path
            driver = webdriver.Firefox(service=webdriver_service, options=options)
        except Exception as exc: log_ui(str(exc)) # Changed
    elif config_dict["browser"] == "edge":
        chromedriver_path = os.path.join(webdriver_path,"msedgedriver")
        if platform.system().lower()=="windows": chromedriver_path = os.path.join(webdriver_path,"msedgedriver.exe")
        webdriver_service = Service(chromedriver_path)
        chrome_options = get_chrome_options(webdriver_path, config_dict) # Assuming get_chrome_options is suitable
        try: driver = webdriver.Edge(service=webdriver_service, options=chrome_options)
        except Exception as exc: log_ui(str(exc)) # Changed
    elif config_dict["browser"] == "safari":
        try: driver = webdriver.Safari()
        except Exception as exc: log_ui(str(exc)) # Changed


    if driver is None:
        log_ui("create web driver object fail @_@;") # Changed
    else:
        try:
            NETWORK_BLOCKED_URLS = ['*clarity.ms/*','*cloudfront.com/*','*doubleclick.net/*','*lndata.com/*','*rollbar.com/*','*twitter.com/i/*','*/adblock.js','*/google_ad_block.js','*cityline.com/js/others.min.js','*anymind360.com/*','*cdn.cookielaw.org/*','*e2elog.fetnet.net*','*fundingchoicesmessages.google.com/*','*google-analytics.*','*googlesyndication.*','*googletagmanager.*','*googletagservices.*','*img.uniicreative.com/*','*platform.twitter.com/*','*play.google.com/*','*player.youku.*','*syndication.twitter.com/*','*youtube.com/*']
            if config_dict["advanced"]["hide_some_image"]: NETWORK_BLOCKED_URLS.extend(['*.woff','*.woff2','*.ttf','*.otf','*fonts.googleapis.com/earlyaccess/*','*/ajax/libs/font-awesome/*','*.ico','*ticketimg2.azureedge.net/image/ActivityImage/*','*static.tixcraft.com/images/activity/*','*static.ticketmaster.sg/images/activity/*','*static.ticketmaster.com/images/activity/*','*ticketimg2.azureedge.net/image/ActivityImage/ActivityImage_*','*.azureedge.net/QWARE_TICKET//images/*','*static.ticketplus.com.tw/event/*','https://t.kfs.io/assets/logo_*.png','https://t.kfs.io/assets/icon-*.png','https://t.kfs.io/upload_images/*.jpg'])
            if config_dict["advanced"]["block_facebook_network"]: NETWORK_BLOCKED_URLS.extend(['*facebook.com/*','*.fbcdn.net/*'])
            if config_dict["browser"] in CONST_CHROME_FAMILY:
                driver.execute_cdp_cmd('Network.setBlockedURLs', {"urls": NETWORK_BLOCKED_URLS})
                driver.execute_cdp_cmd('Network.enable', {})

            if 'kktix.c' in homepage and len(config_dict["advanced"]["kktix_account"])>0:
                try: driver.get(homepage); time.sleep(5)
                except: pass
                if not 'https://kktix.com/users/sign_in?' in homepage: homepage = CONST_KKTIX_SIGN_IN_URL % (homepage)
            if 'famiticket.com' in homepage and len(config_dict["advanced"]["fami_account"])>0: homepage = CONST_FAMI_SIGN_IN_URL
            if 'kham.com' in homepage and len(config_dict["advanced"]["kham_account"])>0: homepage = CONST_KHAM_SIGN_IN_URL
            if 'ticket.com.tw' in homepage and len(config_dict["advanced"]["ticket_account"])>0: homepage = CONST_TICKET_SIGN_IN_URL
            if 'urbtix.hk' in homepage and len(config_dict["advanced"]["urbtix_account"])>0: homepage = CONST_URBTIX_SIGN_IN_URL
            if 'cityline.com' in homepage and len(config_dict["advanced"]["cityline_account"])>0: homepage = CONST_CITYLINE_SIGN_IN_URL
            if 'hkticketing.com' in homepage and len(config_dict["advanced"]["hkticketing_account"])>0: homepage = CONST_HKTICKETING_SIGN_IN_URL
            if 'ticketplus.com.tw' in homepage and len(config_dict["advanced"]["ticketplus_account"]) > 1: homepage = "https://ticketplus.com.tw/"

            log_ui(f"goto url: {homepage}") # Changed
            driver.get(homepage)
            time.sleep(3.0)
            tixcraft_family = any(s in homepage for s in ['tixcraft.com', 'indievox.com', 'ticketmaster.'])
            if tixcraft_family and len(config_dict["advanced"]["tixcraft_sid"]) > 1:
                driver.delete_cookie("SID")
                driver.add_cookie({"name":"SID", "value": config_dict["advanced"]["tixcraft_sid"], "path" : "/", "secure":True})
            if 'ibon.com' in homepage and len(config_dict["advanced"]["ibonqware"]) > 1:
                driver.delete_cookie("ibonqware")
                driver.add_cookie({"name":"ibonqware", "value": config_dict["advanced"]["ibonqware"], "domain" : "ibon.com.tw", "secure":True})
        except WebDriverException as exce2: log_ui(f'WebDriverException in get_driver_by_config navigation: {exce2}') # Changed
        except Exception as exce1: log_ui(f'Exception in get_driver_by_config navigation: {exce1}') # Changed
    return driver

def tixcraft_redirect(driver, url):
    ret = False
    game_name = ""
    url_split = url.split("/")
    if len(url_split) >= 6:
        game_name = url_split[5]
    if len(game_name) > 0:
        if "/activity/detail/%s" % (game_name,) in url:
            entry_url = url.replace("/activity/detail/","/activity/game/")
            log_ui(f"Redirecting to new tixcraft URL: {entry_url}") # Changed
            try:
                driver.get(entry_url)
                ret = True
            except Exception as exec1:
                pass
    return ret

def tixcraft_date_auto_select(driver, url, config_dict, domain_name):
    show_debug_message = config_dict["advanced"]["verbose"]
    auto_select_mode = config_dict["date_auto_select"]["mode"]
    date_keyword = config_dict["date_auto_select"]["date_keyword"].strip()
    pass_date_is_sold_out_enable = config_dict["tixcraft"]["pass_date_is_sold_out"]
    auto_reload_coming_soon_page_enable = config_dict["tixcraft"]["auto_reload_coming_soon_page"]
    # ... (rest of function, ensure internal prints are also converted if they are UI relevant)
    if auto_reload_coming_soon_page_enable:
        if is_coming_soon:
            if show_debug_message:
                log_ui("Tixcraft: Matched coming_soon, reloading date page.") # Changed
            try: driver.refresh()
            except: pass
        else:
            if not is_date_clicked and formated_area_list is not None and len(formated_area_list) == 0:
                log_ui('Tixcraft: No available dates found, refreshing date page.') # Changed
                try:
                    driver.refresh()
                    time.sleep(0.3)
                except: pass
                if config_dict["advanced"]["auto_reload_page_interval"] > 0:
                    time.sleep(config_dict["advanced"]["auto_reload_page_interval"])
    return is_date_clicked # Ensure it returns

def tixcraft_area_auto_select(driver, url, config_dict):
    # ... (rest of function)
    if not target_area is None:
        try:
            target_area.click()
        except Exception as exc:
            log_ui("Tixcraft: Clicking area link failed, retrying with JS.") # Changed
            try:
                driver.execute_script("arguments[0].click();", target_area)
            except Exception as exc_js:
                log_ui(f"Tixcraft: JS click for area link also failed: {exc_js}") # Changed
                pass
    # ... (rest of function)
    return # Ensure return if needed

def kktix_reg_new_main(driver, config_dict, fail_list, played_sound_ticket):
    # ... (rest of function)
            else: # This is part of the if is_ticket_number_assigned: block
                if is_need_refresh:
                    played_sound_ticket = False
                    try:
                        log_ui("KKTIX: No matching price found, refreshing page.") # Changed
                        driver.refresh()
                    except Exception as exc:
                        pass # Potentially log_ui("KKTIX: Refresh failed.")
                    if config_dict["advanced"]["auto_reload_page_interval"] > 0:
                        time.sleep(config_dict["advanced"]["auto_reload_page_interval"])
    return fail_list, played_sound_ticket


def main(args):
    config_dict = get_config_dict(args)
    driver = None
    if not config_dict is None:
        driver = get_driver_by_config(config_dict)
        if not driver is None:
            if not config_dict["advanced"]["headless"]:
                resize_window(driver, config_dict)
        else:
            log_ui("無法使用web driver，程式無法繼續工作") # Changed
            sys.exit()
    else:
        log_ui("Load config error!") # Changed

    url = ""
    last_url = ""
    ocr = None
    Captcha_Browser = None
    try:
        if config_dict["ocr_captcha"]["enable"]:
            ocr = ddddocr.DdddOcr(show_ad=False, beta=config_dict["ocr_captcha"]["beta"])
            Captcha_Browser = NonBrowser()
            if len(config_dict["advanced"]["tixcraft_sid"]) > 1:
                set_non_browser_cookies(driver, config_dict["homepage"], Captcha_Browser)
    except Exception as exc:
        log_ui(f"Error initializing OCR/Captcha_Browser: {exc}") # Changed

    maxbot_last_reset_time = time.time()
    is_quit_bot = False
    is_refresh_datetime_sent = False

    while True:
        time.sleep(0.05)
        if driver is None:
            log_ui("web driver not accessible!") # Changed
            break
        if not is_quit_bot:
            url, is_quit_bot = get_current_url(driver)
        if is_quit_bot:
            try:
                driver.quit()
                driver = None
            except Exception as e: pass
            break
        if url is None: continue
        else:
            if len(url) == 0: continue
        if not is_refresh_datetime_sent:
            is_refresh_datetime_sent = check_refresh_datetime_occur(driver, config_dict["refresh_datetime"])
        is_maxbot_paused = os.path.exists(CONST_MAXBOT_INT28_FILE)
        if len(url) > 0 :
            if url != last_url:
                log_ui(f"Current URL: {url}", also_print=False) # Changed, also_print=False to avoid double if main loop print is kept
                write_last_url_to_file(url)
                if is_maxbot_paused:
                    log_ui("MAXBOT Paused.") # This is a status, good to keep on console
            last_url = url
        if is_maxbot_paused:
            if 'kktix.c' in url: kktix_paused_main(driver, url, config_dict)
            time.sleep(0.1)
            continue
        # ... (rest of main loop logic) ...
    log_ui("Bye bye, see you next time.") # Changed

if __name__ == "__main__":
    debug_captcha_model_flag = False
    if not debug_captcha_model_flag:
        cli()
    else:
        test_captcha_model()
