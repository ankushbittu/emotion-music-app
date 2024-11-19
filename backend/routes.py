import google.generativeai as genai
import os
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from flask_cors import CORS  # Added for CORS
from models import User
from extensions import db
from tensorflow.keras.models import load_model
import numpy as np
import cv2
import logging
from flask_jwt_extended import create_access_token

# Setting up blueprint and logging
main = Blueprint('main', __name__)
CORS(main)  # Allow CORS for all routes under 'main'
logging.basicConfig(level=logging.DEBUG)

@main.route('/')
def home():
    return "Backend is working!"

@main.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "User already exists"}), 400

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User registered successfully"}), 201

@main.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"msg": "Invalid email or password"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token), 200

# Load environment variables from .env file
load_dotenv()

# Load the Gemini API key from the .env file
gemini_api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=gemini_api_key)

# Load the trained CNN model
model_path = "C:/Users/HP BITTU/Downloads/emotion_basic.keras"
model = load_model(model_path)

# Load Haar Cascade for face detection
face_cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(face_cascade_path)

# Define the emotion labels
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

# Updated function to call Gemini API
def get_llm_response(prompt):
    try:
        # Configure the model
        model = genai.GenerativeModel('gemini-pro')
        
        # Create the chat
        chat = model.start_chat(history=[])
        
        # Get the response
        response = chat.send_message(prompt)
        logging.debug(f"LLM Response: {response.text}")
        
        return response.text
    except Exception as e:
        logging.error(f"Error calling LLM API: {e}")
        return None

@main.route('/emotion/detect_emotion', methods=['POST'])
def detect_emotion():
    data = request.form
    image_file = request.files.get('image')

    if not image_file or not data.get('artist') or not data.get('language'):
        logging.error("Missing image, artist, or language")
        return jsonify({"error": "Missing image, artist, or language"}), 400

    try:
        # Convert the image using OpenCV
        image_bytes = image_file.read()  # Read the image file
        logging.debug("Image bytes read successfully")
        
        image_array = np.frombuffer(image_bytes, np.uint8)  # Convert to numpy array
        logging.debug("Image converted to numpy array successfully")

        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)  # Decode image from bytes
        if image is None:
            logging.error("Failed to decode image")
            return jsonify({"error": "Invalid image format"}), 400

        # Convert to grayscale
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        logging.debug("Image converted to grayscale successfully")

        # Detect the face in the image using Haar Cascade
        faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        if len(faces) == 0:
            logging.warning("No face detected in the image")
            return jsonify({"error": "No face detected in the image"}), 400

        # Assuming only one face, take the first detected face
        x, y, w, h = faces[0]
        logging.debug(f"Face detected at coordinates: x={x}, y={y}, w={w}, h={h}")

        # Extract the region of interest (the face)
        face = gray_image[y:y+h, x:x+w]

        # Resize the face to 48x48 (or the required size)
        resized_face = cv2.resize(face, (48, 48))
        logging.debug("Face resized successfully")

        # Normalize pixel values to be between 0 and 1
        normalized_face = resized_face / 255.0

        # Add an extra dimension to match the expected input shape (batch size, height, width, channels)
        face_array = np.expand_dims(normalized_face, axis=0)  # Add batch dimension
        face_array = np.expand_dims(face_array, axis=-1)  # Add channel dimension for grayscale

        # Predict the emotion using the CNN model
        predictions = model.predict(face_array)
        logging.info(f"Model prediction: {predictions}")

        # Get the predicted emotion with the highest probability
        predicted_emotion = emotion_labels[np.argmax(predictions)]
        logging.info(f"Predicted Emotion: {predicted_emotion}")

        # Get artist and language from the form data
        artist = data.get('artist')
        language = data.get('language')

        # Create the LLM prompt for the detected emotion
        prompt = f"""
        The user is feeling {predicted_emotion} based on facial expression analysis. 
        They prefer songs in {language} and like artists such as {artist}. 
        Provide a detailed emotional profile and suggest music themes or specific song recommendations that would suit their mood.
        """
        logging.debug(f"Prompt for LLM: {prompt}")

        # Get response from the LLM using Gemini
        llm_output = get_llm_response(prompt)
        if llm_output is None:
            logging.error("Failed to get response from LLM")
            return jsonify({"error": "Failed to get response from LLM"}), 500

        return jsonify({
            "success": True,
            "emotion_detected": predicted_emotion,
            "detailed_emotion": llm_output
        })

    except Exception as e:
        logging.error(f"Unexpected error during emotion detection: {e}")
        return jsonify({
            "success": False,
            "error": f"Unexpected error during emotion detection: {str(e)}"
        }), 500
