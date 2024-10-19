FILE_ID = 1VL6PRZtTBv9A-_DE54OUk8B2_dYUbP2_
OUTPUT = multimodal_model_complete.pth

# Target to install the dependencies, including gdown
install:
	    pip install gdown

# Target to download the model
download_model:
	    gdown https://drive.google.com/uc?id=$(FILE_ID) -O $(OUTPUT)

# Target to set up the project
setup: install download_model
	    echo "Project setup complete. Model downloaded to $(OUTPUT)."
