FILE_ID = 1iVrGxIhVfXsyRFCshMUNLZn7kXjMRNXM
OUTPUT = multimodal_model_offensive_meme_v3.pth

# Target to install the dependencies, including gdown
install:
	    pip install gdown

# Target to download the model
download_model:
	    gdown https://drive.google.com/uc?id=$(FILE_ID) -O $(OUTPUT)

# Target to set up the project
setup: install download_model
	    echo "Project setup complete. Model downloaded to $(OUTPUT)."
