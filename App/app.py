import random
import time
from flask import Flask, request, jsonify
import base64
from PIL import Image
import io
import gradio as gr
import threading
import hashlib
import torch
import pytesseract
import easyocr
# Import model components from model.py
from model import preprocess_image, preprocess_text , bert_model, resnet_model, additional_layers   

app = Flask(__name__)

useMock = False
# In-memory dictionary for storing images and results
stored_data = {}

# Initialize the OCR reader with the languages you need (e.g., English)
reader = easyocr.Reader(['en'])

# Create a threading lock for model predictions
model_lock = threading.Lock()

# Mock function for processing
def mock_process_image(img):
    prediction = random.choice(['offensive', 'not offensive'])
    return prediction

# Function for processing meme
def process_image(img):
    # Preprocess the image
    image_tensor = preprocess_image(img)  # Shape: (1, 3, 224, 224)

    # Extract text from the image using EasyOCR
    result = reader.readtext(img)

    # Combine all extracted text into a single string for simplicity
    extracted_text = ' '.join([text for (_, text, _) in result])

    print(extracted_text)

    # If no text is extracted, you can assign a default value or handle accordingly
    if not extracted_text.strip():
        extracted_text = ' '  # Or any default text you prefer Assign empty

    # Preprocess the extracted text
    input_ids, attention_mask = preprocess_text(extracted_text)  # Shapes: (1, max_length)

    with model_lock:
        bert_model.eval()
        resnet_model.eval()
        additional_layers.eval()

        with torch.no_grad():
            # Process text with DistilBERT
            text_output = bert_model(input_ids=input_ids, attention_mask=attention_mask)
            text_embedding = text_output.last_hidden_state[:, 0, :]  # Shape: (1, 768)

            # Process image with ResNet50
            image_embedding = resnet_model(image_tensor)  # Shape: (1, 2048)

            # Combine embeddings
            combined_output = torch.cat((text_embedding, image_embedding), dim=1)  # Shape: (1, 2816)

            # Pass through additional layers
            logits = additional_layers(combined_output).squeeze()  # Shape: (1,)

            # Apply sigmoid to get probability
            probability = torch.sigmoid(logits).item()
            print(f"Probability: {probability}")

    # Determine the prediction based on a threshold
    prediction = 'offensive' if probability >= 0.012 else 'not offensive'

    return prediction

# Route for processing with real data
@app.route('/process-meme', methods=['POST'])
def process_meme():
    data = request.json
    img_data = base64.b64decode(data['image'])
    img = Image.open(io.BytesIO(img_data))

     # Compute the image hash
    image_hash = compute_image_hash(img)

    # Check if the image has been processed before
    if image_hash in stored_data and not data.get('re_analyze', False):        # Image has been processed before
        existing_result = stored_data[image_hash]['result']
        # Return a message indicating this and ask if re-analysis is desired
        return jsonify({
            'result': existing_result,
            'message': 'This image has been analyzed before.',
            'hash': image_hash,
            're_analyze': True  # Indicate that re-analysis is possible
        })
    else:
        # Proceed with processing
        if useMock:
            print("Using Mock")
            prediction = mock_process_image(img)
        else:
            prediction = process_image(img)

        # Store the image and result
        store_image(img, prediction, image_hash)

        # Return the prediction to the extension
        return jsonify({'result': prediction})

# Function to compute the SHA-256 hash of an image
def compute_image_hash(img):
    # Ensure the image is in a consistent format
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Convert image to bytes
    buffered = io.BytesIO()
    img.save(buffered, format='PNG')  # Use PNG to avoid compression artifacts
    img_bytes = buffered.getvalue()
    
    # Compute the SHA-256 hash
    sha256 = hashlib.sha256()
    sha256.update(img_bytes)
    image_hash = sha256.hexdigest()
    
    return image_hash


# Function to store image and result
def store_image(img, result, image_hash):
    global stored_data  # Access the global dictionary

    # Convert image to 'RGB' mode if it's not already
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # Convert image to base64 for storage
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

    # Store the image and result in the dictionary
    stored_data[image_hash] = {'image': img_str, 'result': result}

# Function to retrieve images and results from the map
def get_images():
    images = []
    for key, data in stored_data.items():
        img_str = data['image']
        result = data['result']

        # Decode the base64 string back to an image
        img_data = base64.b64decode(img_str)
        img = Image.open(io.BytesIO(img_data))

        # Add a caption or overlay with the result
        images.append((img, f"Result: {result}"))
    return images

# Function to render the image gallery
def show_gallery():
    images = get_images()
    gallery = []
    for img, caption in images:
        gallery.append((img, caption))
    return gallery

# Refresh button action
def refresh_gallery():
    return show_gallery()

# Gradio interface
def create_gradio_interface():
    with gr.Blocks() as demo:
        with gr.Column():
            gr.Markdown("# Meme Moderation Gallery")
            gallery = gr.Gallery(label="Processed Memes", columns=3, height='auto', value=show_gallery())
            refresh_button = gr.Button("Refresh")

            # Set initial gallery state
            #gallery.update(value=show_gallery())

            # Refresh action
            refresh_button.click(refresh_gallery, outputs=gallery)

    return demo

# Run Flask app and Gradio app together
def run_app():
    # Run Flask app in a separate thread
    threading.Thread(target=lambda: app.run(port=5000, debug=False, use_reloader=False)).start()

    # Launch Gradio interface
    demo = create_gradio_interface()
    demo.launch(server_port=7865, share=True)

if __name__ == '__main__':
    run_app()
