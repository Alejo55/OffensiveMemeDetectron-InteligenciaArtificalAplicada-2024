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
            // Show a notification with the result
            showNotification('Meme Analysis Result', 'The meme is ' + data.result);
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error processing image');
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

// Mocked backend response function
function mockBackendResponse(base64Image) {
    let isOffensive = Math.random() < 0.5 ? "offensive" : "not offensive";

    // Show a notification with the result
    showNotification('Meme Analysis Result', 'The meme is ' + isOffensive);
}
