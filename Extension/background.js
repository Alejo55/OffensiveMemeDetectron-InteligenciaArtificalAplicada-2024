const useMockedBackend = false;

chrome.action.onClicked.addListener((tab) => {
    // Inject contentScript.js into the active tab
    chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ['contentScript.js']
    });
});

// Listener to receive messages from contentScript.js
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log('Message received:', message);  // Debug message to see the incoming message
    // Check if the message contains an image URL and call fetchImage
    if (message.type === 'FETCH_IMAGE' && message.imageUrl) {
        fetchImage(message.imageUrl);  // Pass the imageUrl to fetchImage
    } else {
        console.error('No image URL provided in the message.');
    }
});

function fetchImage(imageUrl) {
    console.log("Fetching image from URL:", imageUrl);
    // Fetch the image as a Blob using the Fetch API
    fetch(imageUrl)
        .then(response => response.blob())
        .then(blob => {
            const reader = new FileReader();
            reader.onloadend = function () {
                const base64Image = reader.result.split(',')[1];  // Get base64 string

                if (useMockedBackend) {
                    // Mocked backend response
                    mockBackendResponse(base64Image);
                } else {
                    // Send the image to the Flask backend
                    processMemeImage(base64Image);
                }

            };
            reader.readAsDataURL(blob);
        })
        .catch(error => {
            console.error('Error fetching image:', error);
        });
}

function processMemeImage(base64Image) {
    fetch('http://127.0.0.1:5000/process-meme', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: base64Image })
    })
        .then(response => response.json())
        .then(data => {

            if (data.re_analyze) {   // Check if the image has already been analyzed 
                createReanalyzeNotification({ image: base64Image, message: 'This meme has already been analyzed.' });
                return;
            }   

            // Show a notification with the result
            showNotification('Meme Analysis Result', 'The meme is ' + data.result);
        })
        .catch(error => {
            showNotification('Error processing image', error.message);
        });
}

// Function to show a Chrome notification
function showNotification(title, message) {
    var icon = 'POGE.png';
    if (message === "offensive") {
        icon = 'POGE-angry.png';
    }

    chrome.notifications.create({
        type: 'basic',
        iconUrl: 'POGE-angry.png',  // Path to your extension icon
        title: title,
        message: message
    });
}

function createReanalyzeNotification(data) {
    // Generate a unique notification ID
    const notificationId = 'reanalyze-' + Date.now();

    // Store the data associated with this notification
    pendingNotifications[notificationId] = data;

    chrome.notifications.create(notificationId, {
        type: 'basic',
        iconUrl: 'POGE-main.png', // Path to your extension's icon
        title: 'Image Already Analyzed',
        message: data.message + ' Do you want to re-analyze it?',
        buttons: [
            { title: 'Yes! Re-analyze' },
            { title: 'No' }
        ],
        priority: 0
    });
}

// Object to keep track of pending notifications and their associated data
const pendingNotifications = {};

chrome.notifications.onButtonClicked.addListener(function (notificationId, buttonIndex) {
    if (notificationId.startsWith('reanalyze-')) {
        const data = pendingNotifications[notificationId];
        if (data) {
            if (buttonIndex === 0) {
                // User clicked 'Re-analyze'
                fetch('http://127.0.0.1:5000/process-meme', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 'image': data.image, 're_analyze': true })
                })
                    .then(response => response.json())
                    .then(resultData => {
                        // Handle the new result
                        showNotification('New Analysis Result', resultData.result);
                        // Remove the notification data
                        delete pendingNotifications[notificationId];
                        // Clear the notification
                        chrome.notifications.clear(notificationId);
                    });
            } else if (buttonIndex === 1) {
                // User clicked 'Use Existing Result'
                showNotification('Existing Analysis Result', data.result);
                // Remove the notification data
                delete pendingNotifications[notificationId];
                // Clear the notification
                chrome.notifications.clear(notificationId);
            }
        }
    }
});

// Optional: Handle when the notification is closed
chrome.notifications.onClosed.addListener(function (notificationId, byUser) {
    if (pendingNotifications[notificationId]) {
        delete pendingNotifications[notificationId];
    }
});


// Mocked backend response function
function mockBackendResponse(base64Image) {
    let isOffensive = Math.random() < 0.5 ? "offensive" : "not offensive";

    // Show a notification with the result
    showNotification('Meme Analysis Result', 'The meme is ' + isOffensive);
}
