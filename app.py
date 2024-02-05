from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image, ImageFilter
import easyocr
import io
import base64
from ultralytics import YOLO

model = YOLO('best.pt')
app = Flask(__name__)
CORS(app)

def save_base64_image(base64_string, file_extension='jpeg'):
    image_bytes = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(image_bytes))
    temp_file_path = f'temp_image.{file_extension}'
    image.save(temp_file_path)
    return temp_file_path

def crop_and_base64_objects(image, results):
    base64_images = []
    if results:
        for i, result in enumerate(results):
            box = result.boxes[0].xyxy[0].tolist()
            xmin, ymin, xmax, ymax = map(int, box)
            cropped_image = image.crop((xmin, ymin, xmax, ymax))

            buffered = io.BytesIO()
            cropped_image.save(buffered, format="jpeg")
            base64_string = base64.b64encode(buffered.getvalue()).decode('utf-8')
            base64_images.append(base64_string)

    return base64_images

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
        image = Image.open(io.BytesIO(image_bytes))
        results = model(image)

        base64_images = crop_and_base64_objects(image, results)

        for base64_image in base64_images:
            image_bytes2 = base64.b64decode(base64_image)
            image2 = Image.open(io.BytesIO(image_bytes2))
            

            
        print(base64_images)
        image_format = image.format.lower() if image.format else None
        allowed_characters = set('0123456789กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรลวศษสหฬอฮ๐๑๒๓๔๕๖๗๘๙')


        reader = easyocr.Reader(['th'])
        ocr_result = reader.readtext(image)

        recognized_texts = ["".join(char for char in text_info[1] if char in allowed_characters) for text_info in ocr_result]
        print('Recognized texts:', recognized_texts)
        return jsonify({"recognized_texts": recognized_texts, "image_format": image_format, "base64_images": base64_images})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()
