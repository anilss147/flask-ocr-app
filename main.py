from flask import Flask, render_template, request, jsonify
import pytesseract
from PIL import Image
import os
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure Tesseract OCR path (update this path if Tesseract is installed elsewhere)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Verify Tesseract path
if not os.path.exists(pytesseract.pytesseract.tesseract_cmd):
    logger.error("Tesseract executable not found at the specified path.")
    raise FileNotFoundError("Tesseract executable not found. Please check the path.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        logger.warning("No file part in the request.")
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['image']
    if file.filename == '':
        logger.warning("No file selected for upload.")
        return jsonify({'error': 'No file selected'}), 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    logger.info(f"File saved to {filepath}")

    try:
        # Perform OCR on the uploaded image
        text = pytesseract.image_to_string(Image.open(filepath))
        logger.info("OCR processing completed successfully.")
        return jsonify({'text': text})
    except Exception as e:
        logger.error(f"Error during OCR processing: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up the uploaded file
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Temporary file {filepath} removed.")

if __name__ == '__main__':
    try:
        app.run(debug=True, port=5001)
    except Exception as e:
        logger.error(f"Failed to start the Flask application: {e}")