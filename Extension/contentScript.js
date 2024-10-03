{
    // Fetch the first image on the page
    let imageElement = document.querySelector('[alt="Image"]');

    if (imageElement) {
        let imageUrl = imageElement.src;
        console.log("Found the image URL:", imageUrl);

        // Send the image URL to the background script (service worker)
        chrome.runtime.sendMessage({ type: 'FETCH_IMAGE', imageUrl: imageUrl });
        console.log("Content Script - Message sent successfully.");
    } else {
        alert("No image found on the page.");
    }

}
