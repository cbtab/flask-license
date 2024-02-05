from flask import Flask, request, jsonify
from ultralytics import YOLO
from PIL import Image, ImageFilter
import easyocr
import io
import base64
import os

app = Flask(__name__)

model = YOLO('best.pt')

@app.route('/process_image', methods=['POST'])
def process_image():
    try:

        base64_image = request.json['image']

        image_bytes = base64.b64decode(base64_image)


        image_path = 'received_image.png'
        with open(image_path, 'wb') as image_file:
            image_file.write(image_bytes)


        results = model(image_path)
        boxes = results[0].boxes

        if len(boxes) > 0:
            box = boxes[0]
            xmin, ymin, xmax, ymax = box.xyxy[0].tolist()

            image = Image.open(image_path)
            cropped_image = image.crop((xmin, ymin, xmax, ymax))
            sharpened_image = cropped_image.filter(ImageFilter.SHARPEN)

    
            sharpened_image_path = 'sharpened_image.png'
            sharpened_image.save(sharpened_image_path)

            reader = easyocr.Reader(['th'])
            ocr_result = reader.readtext(sharpened_image_path)
        else:
            image = Image.open(image_path)

            reader = easyocr.Reader(['th'])
            ocr_result = reader.readtext(image_path)

        recognized_texts = [text_info[1] for text_info in ocr_result]
        print(recognized_texts)
        return jsonify({"recognized_texts": recognized_texts})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(image_path):
            os.remove(image_path)
        if os.path.exists(sharpened_image_path):
            os.remove(sharpened_image_path)

if __name__ == '__main__':
    app.run(debug=True)
