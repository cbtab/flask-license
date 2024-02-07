from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import easyocr

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def hello_world():
    return "Server is running"

@app.route('/process_image', methods=['POST'])
def process_image():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image provided"}), 400

        uploaded_image = request.files['image']

        with Image.open(uploaded_image) as image:
            image_format = image.format.lower() if image.format else None

            reader = easyocr.Reader(['th'])
            ocr_result = reader.readtext(image)

            recognized_texts = [text_info[1] for text_info in ocr_result]
            print('Recognized texts:', recognized_texts)

        return jsonify({"recognized_texts": recognized_texts, "image_format": image_format, "server_message": "Image processed successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
