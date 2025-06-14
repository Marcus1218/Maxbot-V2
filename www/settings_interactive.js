// New UI element selectors from settings.html (ensure these IDs exist)
const bot_question_area_interactive = document.querySelector('#bot-question-area');
const bot_question_text_interactive = document.querySelector('#bot-question-text');
const bot_answer_input_interactive = document.querySelector('#bot-answer-input');
const submit_bot_answer_btn_interactive = document.querySelector('#submit-bot-answer-btn');
const bot_answer_feedback_interactive = document.querySelector('#bot-answer-feedback');
const pause_resume_feedback_interactive = document.querySelector('#pause_resume_feedback');
const bot_log_display_interactive = document.querySelector('#bot-log-display');

// Helper function for pause/resume feedback
let pauseResumeFeedbackTimer_interactive;
function showPauseResumeFeedback_interactive(msg, isError = false) {
    clearTimeout(pauseResumeFeedbackTimer_interactive);
    if (pause_resume_feedback_interactive) {
        pause_resume_feedback_interactive.textContent = msg;
        pause_resume_feedback_interactive.className = isError ? 'ms-3 text-danger' : 'ms-3 text-warning';
        pauseResumeFeedbackTimer_interactive = setTimeout(() => {
            if (pause_resume_feedback_interactive) {
                pause_resume_feedback_interactive.textContent = '';
            }
        }, 3000);
    }
}

// Function to fetch bot questions
function maxbot_fetch_question_api_interactive() {
    let question_api_url = "http://127.0.0.1:16888/get_question"; // Requires this endpoint on backend
    $.get(question_api_url)
        .done(function(data) {
            if (bot_question_area_interactive && bot_question_text_interactive) {
                if (data && data.question && data.question.trim() !== "") {
                    bot_question_text_interactive.textContent = data.question;
                    bot_question_area_interactive.style.display = '';
                    if (bot_answer_feedback_interactive) bot_answer_feedback_interactive.textContent = '';
                } else {
                    bot_question_text_interactive.textContent = '';
                    bot_question_area_interactive.style.display = 'none';
                }
            }
        })
        .fail(function() {
            // console.error("Error fetching bot question.");
            if (bot_question_area_interactive) bot_question_area_interactive.style.display = 'none';
        });
}

// Event listener for submitting bot answers
if (submit_bot_answer_btn_interactive) {
    submit_bot_answer_btn_interactive.addEventListener('click', function() {
        const answer = bot_answer_input_interactive.value.trim();
        if (!answer) {
            if (bot_answer_feedback_interactive) {
                bot_answer_feedback_interactive.textContent = 'Please enter an answer.';
                bot_answer_feedback_interactive.className = 'form-text text-danger';
            }
            return;
        }
        if (bot_answer_feedback_interactive) {
            bot_answer_feedback_interactive.textContent = 'Submitting...';
            bot_answer_feedback_interactive.className = 'form-text text-info';
        }

        let submit_answer_api_url = "http://127.0.0.1:16888/submit_answer"; // Requires this endpoint
        $.post(submit_answer_api_url, JSON.stringify({ answer: answer }))
            .done(function(data) {
                if (bot_answer_feedback_interactive) {
                    bot_answer_feedback_interactive.textContent = data.message || 'Answer submitted successfully!';
                    bot_answer_feedback_interactive.className = 'form-text text-success';
                }
                if (bot_answer_input_interactive) bot_answer_input_interactive.value = '';
                // setTimeout(maxbot_fetch_question_api_interactive, 500);
            })
            .fail(function() {
                if (bot_answer_feedback_interactive) {
                    bot_answer_feedback_interactive.textContent = 'Error submitting answer.';
                    bot_answer_feedback_interactive.className = 'form-text text-danger';
                }
            });
    });
}

function maxbot_fetch_logs_api_interactive() {
    if (!bot_log_display_interactive) return;

    let logs_api_url = "http://127.0.0.1:16888/get_logs";
    $.get(logs_api_url)
        .done(function(data) {
            if (data && Array.isArray(data.logs)) {
                const logContent = data.logs.join('\n'); // Logs are already strings
                bot_log_display_interactive.textContent = logContent;
                bot_log_display_interactive.scrollTop = bot_log_display_interactive.scrollHeight;
            }
        })
        .fail(function() {
            // bot_log_display_interactive.textContent = "Error fetching logs.";
        });
}

// Overriding/Patching functions from settings.js
// We need to ensure this script runs AFTER settings.js

// Store original functions if they exist, then override
var original_maxbot_pause_api = window.maxbot_pause_api;
window.maxbot_pause_api = function() {
    showPauseResumeFeedback_interactive("Pause command sent...", false);
    let api_url = "http://127.0.0.1:16888/pause";
    // Assuming 'settings' is a global variable from settings.js
    if(typeof settings !== 'undefined' && settings) {
        $.get( api_url, function() {})
        .done(function(data) {
            showPauseResumeFeedback_interactive("Pause command successful.", false);
        })
        .fail(function() {
            showPauseResumeFeedback_interactive("Pause command failed.", true);
        });
    } else {
         showPauseResumeFeedback_interactive("Settings not loaded, cannot pause.", true);
    }
}

var original_maxbot_resume_api = window.maxbot_resume_api;
window.maxbot_resume_api = function() {
    showPauseResumeFeedback_interactive("Resume command sent...", false);
    let api_url = "http://127.0.0.1:16888/resume";
    if(typeof settings !== 'undefined' && settings) {
        $.get( api_url, function() {})
        .done(function(data) {
            showPauseResumeFeedback_interactive("Resume command successful.", false);
        })
        .fail(function() {
            showPauseResumeFeedback_interactive("Resume command failed.", true);
        });
    } else {
        showPauseResumeFeedback_interactive("Settings not loaded, cannot resume.", true);
    }
}

var original_maxbot_status_api = window.maxbot_status_api;
window.maxbot_status_api = function() {
    let api_url = "http://127.0.0.1:16888/status";
    $.get( api_url, function() {})
    .done(function(data) {
        let status_text = "已暫停";
        let status_class = "badge text-bg-danger";
        if(data.status) {
            status_text="已啟動";
            status_class = "badge text-bg-success";
            $("#pause_btn").removeClass("disappear");
            $("#resume_btn").addClass("disappear");
        } else {
            $("#pause_btn").addClass("disappear");
            $("#resume_btn").removeClass("disappear");
        }
        // Corrected to use .val() for input field, assuming last_url is an input
        const lastUrlInput = document.querySelector('#last_url');
        if (lastUrlInput) lastUrlInput.value = data.last_url;

        $("#maxbot_status").html(status_text).prop( "class", status_class);
    })
    .fail(function() {
        // console.error("Status API failed");
    });
}

// Clear the original interval from settings.js and set a new one
if (typeof status_interval !== 'undefined') {
    clearInterval(status_interval);
}

var status_interval_interactive = setInterval(() => {
    if (typeof maxbot_status_api === 'function') { // Check if original or new is defined
        maxbot_status_api(); // This will call the new (overridden) version
    }
    maxbot_fetch_question_api_interactive();
    maxbot_fetch_logs_api_interactive(); // Added this line
    if (typeof update_system_time === 'function') {
        update_system_time();
    }
}, 1000);

// The original run_message for the run button might still be in settings.js
// If it needs updating, it should also be patched or redefined here.
// For now, assuming it's okay or will be handled if issues arise.

console.log("settings_interactive.js loaded");
