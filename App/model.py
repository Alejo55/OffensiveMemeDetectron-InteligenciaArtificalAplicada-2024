# Import necessary libraries
import torch
from transformers import DistilBertTokenizer, DistilBertModel
from torchvision import models, transforms
import torch.nn as nn
from PIL import Image
import re
import os

# Initialize the models
def build_multimodal_model():
    # Load DistilBERT
    bert_model = DistilBertModel.from_pretrained('distilbert-base-uncased')
    # Load ResNet50
    resnet_model = models.resnet50(weights='IMAGENET1K_V1')
    resnet_model.fc = nn.Identity()  # Remove the final fully connected layer

    # Define additional layers (ensure it matches your training)
    additional_layers = nn.Sequential(
        nn.Linear(768 + 2048, 1536),
        nn.BatchNorm1d(1536),
        nn.LeakyReLU(negative_slope=0.01),
        nn.Dropout(p=0.3),
        nn.Linear(1536, 768),
        nn.BatchNorm1d(768),
        nn.LeakyReLU(negative_slope=0.01),
        nn.Dropout(p=0.4),
        nn.Linear(768, 256),
        nn.BatchNorm1d(256),
        nn.LeakyReLU(negative_slope=0.01),
        nn.Dropout(p=0.5),
        nn.Linear(256, 1)
    )

    return bert_model, resnet_model, additional_layers

# Build the model
bert_model, resnet_model, additional_layers = build_multimodal_model()

# Load the saved state dictionaries
print(os.getcwd())
checkpoint = torch.load('multimodal_model_offensive_meme_v2.pth', map_location=torch.device('cpu'))

bert_model.load_state_dict(checkpoint['bert_model'])
resnet_model.load_state_dict(checkpoint['resnet_model'])
additional_layers.load_state_dict(checkpoint['add_layers'])

# Set models to evaluation mode
bert_model.eval()
resnet_model.eval()
additional_layers.eval()

# Move models to appropriate device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
bert_model.to(device)
resnet_model.to(device)
additional_layers.to(device)

# Define the image transformations
image_transform = transforms.Compose([
    transforms.Resize((224, 224)),  # Resize to 224x224 pixels
    transforms.ToTensor(),          # Convert to tensor
    transforms.Normalize(           # Normalize using ImageNet's mean and std
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

def preprocess_image(image):
    # Ensure the image is in RGB format
    if image.mode != 'RGB':
        image = image.convert('RGB')
    # Apply transformations
    image_tensor = image_transform(image)
    # Add batch dimension
    image_tensor = image_tensor.unsqueeze(0)  # Shape: (1, 3, 224, 224)
    return image_tensor.to(device)


# Load the tokenizer
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')

def preprocess_text(text, max_length=128):
    # Clean the text
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)  # Replace multiple whitespace with a single space

    # Additional cleaning if necessary
    # e.g., remove non-ASCII characters, unwanted symbols, etc.

    # Tokenize and encode the text
    encoding = tokenizer.encode_plus(
        text,
        add_special_tokens=True,
        max_length=max_length,
        return_token_type_ids=False,
        padding='max_length',
        truncation=True,
        return_attention_mask=True,
        return_tensors='pt',
    )
    input_ids = encoding['input_ids'].to(device)
    attention_mask = encoding['attention_mask'].to(device)
    return input_ids, attention_mask

