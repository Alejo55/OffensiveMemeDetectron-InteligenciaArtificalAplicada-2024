document.getElementById('fetchButton').addEventListener('click', function() {
    // Get the active tab and inject the content script into it
    chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
        chrome.scripting.executeScript({
            target: { tabId: tabs[0].id },
            files: ['contentScript.js']
        });
    });
});
