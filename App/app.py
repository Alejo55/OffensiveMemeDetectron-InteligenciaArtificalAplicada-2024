import random
import time
from flask import Flask, request, jsonify
import base64
from PIL import Image
import io
import gradio as gr

app = Flask(__name__)

global useMock 
useMock = True 
# In-memory dictionary for storing images and results
stored_data = {}

# Mock function for processing
def mock_process_image(img):
    prediction = random.choice(['offensive', 'not offensive', 'not sure'])  
    return prediction

# Function for processing meme
def process_image(img):
    #
    # TODO: Replace with real processing logic AI/ML model 
    #
    prediction = "Real prediction result"
    return prediction

# Route for processing with real data
@app.route('/process-meme', methods=['POST'])
def process_meme():
    global stored_data  # Access the global dictionary

    data = request.json
    img_data = base64.b64decode(data['image'])
    img = Image.open(io.BytesIO(img_data))

    if useMock:
        # Mock process the image
        prediction = mock_process_image(img)  
    else:
        # Real process the image 
        prediction = process_image(img)

        # Store the image and result
        store_image(img, prediction)  

    # Return the real prediction to extension
    return jsonify({'result': prediction})

# Function to store image and result
def store_image(img, result):
    global stored_data  # Access the global dictionary
    # Convert image to base64 for storage
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

    # Generate a unique key (timestamp-based)
    unique_key = str(time.time())

    # Store the image and result in the dictionary
    stored_data[unique_key] = {'image': img_str, 'result': result}