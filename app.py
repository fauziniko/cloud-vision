from flask import Flask, request, jsonify
from google.cloud import vision
from werkzeug.utils import secure_filename
import io
import os
import re

app = Flask(__name__)

# Set Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ""

# Nutrition synonyms
nutrition_synonyms = {
    "calories": ["calories", "energy", "energies", "kalori", "Energi total"],
    "salt": ["sodium", "salt", "salts", "natrium", "garam", "Garam (Natrium)"],
    "fat": ["fat", "fats", "saturate", "Lemak Total", "saturates"],
    "sugar": ["sugar", "sugars", "gula"],
    "protein": ["protein"]
}

def extract_text_from_image(image_file):
    """Extract text from an image using Google Cloud Vision."""
    client = vision.ImageAnnotatorClient()
    
    image = vision.Image(content=image_file.read())
    response = client.text_detection(image=image)
    texts = response.text_annotations
    if texts:
        return texts[0].description
    else:
        return ""

def extract_nutrition_information(text):
    """Extract specific nutritional information from the text."""
    nutrition_data = {}

    # Search for each type of nutrient in the text
    for key, synonyms in nutrition_synonyms.items():
        for synonym in synonyms:
            pattern = rf"{synonym}\s*[:\-]?\s*(\d+[\.,]?\d*)\s*(g|mg|%)?"
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value_with_unit = f"{match[1].strip()} {match[2].strip() if match[2] else ''}"
                nutrition_data[key] = value_with_unit
                break  # Stop after finding the first match for this nutrient
    
    return nutrition_data

@app.route('/extract', methods=['POST'])
def extract_nutrition():
    if 'file' not in request.files:
        return jsonify({"error": "File tidak ditemukan pada permintaan."}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "Nama file kosong."}), 400
    
    try:
        # Langsung proses file dari memori
        text = extract_text_from_image(file)
        if not text:
            return jsonify({"error": "Tidak ada teks yang ditemukan dalam gambar."}), 400
        
        # Ekstraksi informasi nutrisi
        nutrition_info = extract_nutrition_information(text)
        if nutrition_info:
            return jsonify({"result": nutrition_info}), 200
        else:
            return jsonify({"error": "Informasi nutrisi tidak ditemukan."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080)) 
    app.run(host='0.0.0.0', port=port)
