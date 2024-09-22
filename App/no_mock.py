from flask import Flask, request, jsonify
import torch
from transformers import BertTokenizer, BertModel
from PIL import Image
import io
import base64

app = Flask(__name__)

# Cargar el modelo preentrenado
# Aquí cargamos tanto el modelo de texto como el de imágenes que previamente entrenaste
model_text = BertModel.from_pretrained('bert-base-uncased')

model_image = torch.load('image_model.pth')
model_combined = torch.load('combined_model.pth')

@app.route('/predict', methods=['POST'])
def predict():
    # Recibir la imagen como base64
    data = request.json
    img_data = base64.b64decode(data['image'])
    img = Image.open(io.BytesIO(img_data))

    # Procesar la imagen con el modelo de imagen
    image_features = model_image(img)

    # Procesar el texto con el modelo de texto
    text = data['text']
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    text_features = model_text(**tokenizer(text, return_tensors='pt'))

    # Combinar las características y hacer la predicción
    combined_features = torch.cat((image_features, text_features), dim=1)
    prediction = model_combined(combined_features)

    return jsonify({'prediction': prediction.item()})

if __name__ == '__main__':
    app.run(debug=True)
