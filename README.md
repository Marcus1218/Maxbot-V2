# MaxBot 自動搶票機器人

MaxBot 是一款支援多平台、多網站的自動化搶票工具，支援 KKTIX、拓元、Ticketmaster、全網、udn 售票網等多個售票系統。內建自動驗證碼辨識（OCR）、自動選位、排除關鍵字、瀏覽器自動化等功能，並可透過網頁介面進行設定。

##最新消息⚠️ 此專案已停止更新支援 可以嘗試最新軟件[按此了解](https://github.com/Marcus1218/hkticketkiller-crack)

## 主要功能
- 支援多家售票網站自動搶票
- 自動辨識驗證碼（內建 ddddocr）
- 自動選擇日期、區域、票數
- 支援 Chrome、Edge、Firefox 等瀏覽器
- 可自訂排除區域關鍵字
- 支援多帳號、多視窗自動化
- 內建 Web 設定介面
- 支援 Chrome Extension 擴充

## 安裝方式
1. 下載專案原始碼：
   ```bash
   git clone https://github.com/Marcus1218/Maxbot-V2
   cd Maxbot-V2
   ```
2. 安裝 Python 3.7 以上版本。
3. 安裝必要套件：
   ```bash
   pip install -r requirement.txt
   ```
4. （建議）安裝 Chrome 瀏覽器與對應 chromedriver。
5. 執行 `settings.py` 啟動 Web 設定介面：
   ```bash
   python3 settings.py
   ```
6. 預設會自動開啟 http://127.0.0.1:16888/settings.html 進行設定。

## Docker 部署

你也可以使用 Docker 快速部署 MaxBot：

1. 建立映像檔（於專案根目錄執行）：
   ```bash
   docker build -t maxbot .
   ```
2. 啟動容器：
   ```bash
   docker run -d -p 16888:16888 --name maxbot maxbot
   ```
3. 預設會自動開啟 http://127.0.0.1:16888/settings.html 進行設定。

> 如需自訂設定檔或掛載資料夾，可使用 `-v` 參數掛載本機目錄。

## 目錄結構
- `settings.py`：主程式與 Web 設定伺服器
- `util.py`：共用工具函式
- `NonBrowser.py`：非瀏覽器模式驗證碼處理
- `settings.json`：設定檔
- `webdriver/`：Chrome/Edge 擴充套件
- `www/`：Web 設定介面前端檔案

## 設定說明
- 於 Web 介面設定各項參數（如帳號、密碼、選位模式、排除關鍵字等）
- 支援密碼加密儲存
- 可自訂自動刷新、重載、視窗大小等進階參數

## 支援網站
- KKTIX
- 拓元 tixcraft
- Ticketmaster.sg
- 添翼、全網、udn、年代、寬宏、Cityline、香港快達票、澳門銀河等

## 常見問題
- 啟動後無法自動開啟瀏覽器？請確認已安裝對應瀏覽器與驅動程式。
- 驗證碼辨識錯誤？可於 Web 設定頁面調整 OCR 參數或手動輸入。
- 其他問題請參考 [官方說明](https://max-everyday.com/2018/03/tixcraft-bot/) 或 [GitHub Releases](https://github.com/max32002/tixcraft_bot/releases)

## 授權
本專案採用 MIT License。

---

> 本專案僅供學術研究與自動化學習用途，請勿用於任何違反售票網站規範之行為。
