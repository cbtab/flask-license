from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image, ImageFilter
import easyocr
import io
import base64

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def hello_world():
    return "Server is running"

@app.route('/process_image', methods=['POST'])
def process_image():
    try:
        if 'image' not in request.json:
            return jsonify({"error": "No image provided"}), 400

        base64_image = request.json['image']
        image_bytes = base64.b64decode(base64_image)

        with Image.open(io.BytesIO(image_bytes)) as image:
            image_format = image.format.lower() if image.format else None

            reader = easyocr.Reader(['th'])
            ocr_result = reader.readtext(image)

            recognized_texts = [text_info[1] for text_info in ocr_result]
            print('Recognized texts:', recognized_texts)

        return jsonify({"recognized_texts": recognized_texts, "image_format": image_format, "server_message": "Image processed successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
