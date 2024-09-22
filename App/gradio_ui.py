import gradio as gr
from app import gradio_display_all  # Import the function from your Flask app

# Gradio Interface to display all stored images and results
@app.route('/gradio', methods=['GET'])
def create_gradio_interface():
    return gr.Interface(
        fn=gradio_display_all,
        inputs=None,  # No input needed
        outputs=[gr.Gallery(label="Stored Images"), gr.Textbox(label="Results")],  # Display the images and results
        title="Meme Analyzer",
        description="Displays all processed images and results stored in memory."
    )

# Run the Gradio interface
if __name__ == '__main__':
    create_gradio_interface().launch()
