from flask import Flask, request, jsonify
from keras.models import load_model
from PIL import Image, ImageOps
import numpy as np
from flask_cors import CORS

# Load the model
model = load_model("keras_model.h5", compile=False)

# Load the labels
class_names = open("labels.txt", "r").readlines()

# Initialize Flask app
app = Flask(__name__)

# Enable CORS
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=False,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
)


# Scoring logic based on classification
def get_freshness_details(class_name, confidence):
    """
    Convert class prediction into detailed freshness information
    """
    class_name = class_name.strip().lower()
    
    # Define scoring rules
    scoring_map = {
        'ripe': {
            'score': 95,
            'shelf_life': '5-7 days',
            'action': 'Premium market ready - excellent for immediate sale',
            'pricing': 'Full market price (₦15,000-₦18,000/basket)',
            'urgency': 'low',
            'cooling_needed': False
        },
        'unripe': {
            'score': 70,
            'shelf_life': '3-4 days until peak ripeness',
            'action': 'Good for market - will ripen soon',
            'pricing': 'Standard price (₦12,000-₦15,000/basket)',
            'urgency': 'medium',
            'cooling_needed': False
        },
        'old': {
            'score': 50,
            'shelf_life': '1-2 days maximum',
            'action': 'Sell immediately or move to cold storage',
            'pricing': 'Reduced price (₦8,000-₦10,000/basket)',
            'urgency': 'high',
            'cooling_needed': True
        },
        'damaged': {
            'score': 20,
            'shelf_life': 'Process today',
            'action': 'Not suitable for fresh sale - process into paste/sauce',
            'pricing': 'Processing price only (₦3,000-₦5,000/basket)',
            'urgency': 'critical',
            'cooling_needed': True
        }
    }
    
    # Default fallback if class not recognized
    if class_name not in scoring_map:
        return {
            'score': 50,
            'category': class_name.capitalize(),
            'confidence': float(confidence),
            'shelf_life': 'Unknown',
            'action': 'Manual inspection recommended',
            'pricing': 'Market rate varies',
            'urgency': 'medium',
            'cooling_needed': False
        }
    
    details = scoring_map[class_name]
    
    return {
        'score': details['score'],
        'category': class_name.capitalize(),
        'confidence': float(confidence),
        'shelf_life': details['shelf_life'],
        'action': details['action'],
        'pricing': details['pricing'],
        'urgency': details['urgency'],
        'cooling_needed': details['cooling_needed']
    }


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200


@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get image file from request
        file = request.files['image']

        if not file or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file. Please upload an image file (e.g., PNG, JPEG).'}), 400

        # Open the image file using PIL
        image = Image.open(file.stream).convert("RGB")

        # Preprocess the image
        size = (224, 224)
        resized_img = image.resize(size, resample=Image.LANCZOS)
        image = ImageOps.pad(resized_img, size)
        image_array = np.asarray(image)
        normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        data[0] = normalized_image_array

        # Make prediction
        prediction = model.predict(data)
        index = np.argmax(prediction)
        class_name = class_names[index].strip()[2:]  # Remove index prefix
        confidence_score = prediction[0][index]
        confidence_score = np.round(confidence_score * 100, 2)

        # Get detailed freshness information
        freshness_details = get_freshness_details(class_name, confidence_score)

        return jsonify(freshness_details)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def allowed_file(filename):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5001)