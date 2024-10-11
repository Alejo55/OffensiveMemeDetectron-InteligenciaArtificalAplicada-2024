FILE_ID = 1fPo9JRoLk1MI5fYeB6y7DDi2sl3dBswk
OUTPUT = multimodal_model_offensive_meme_v2.pth

# Target to install the dependencies, including gdown
install:
	    pip install gdown

# Target to download the model
download_model:
	    gdown https://drive.google.com/uc?id=$(FILE_ID) -O $(OUTPUT)

# Target to set up the project
setup: install download_model
	    echo "Project setup complete. Model downloaded to $(OUTPUT)."
