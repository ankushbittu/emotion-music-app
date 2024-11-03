import google.generativeai as genai
import os
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from models import User
from extensions import db
from tensorflow.keras.models import load_model
import numpy as np
from PIL import Image
import io
import base64
from flask_jwt_extended import create_access_token

main = Blueprint('main', __name__)

# Keep existing routes unchanged
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
model_path = "C:/Users/HP BITTU/Downloads/final_model.keras"
model = load_model(model_path)

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
        
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

@main.route('/emotion/detect_emotion', methods=['POST'])
def detect_emotion():
    data = request.form
    image_file = request.files.get('image')

    if not image_file or not data.get('artist') or not data.get('language'):
        return jsonify({"error": "Missing image, artist, or language"}), 400

    # Convert the image to grayscale and resize to 48x48
    image = Image.open(image_file).convert('L')
    image = image.resize((48, 48))
    image = np.array(image).reshape(1, 48, 48, 1) / 255.0

    # Predict the emotion using the CNN model
    predictions = model.predict(image)
    predicted_emotion = emotion_labels[np.argmax(predictions)]

    # Get artist and language from the form data
    artist = data.get('artist')
    language = data.get('language')

    # Create the LLM prompt
    prompt = f"""
    The user is feeling {predicted_emotion} based on facial expression analysis. 
    They prefer songs in {language} and like artists such as {artist}. 
    Provide a detailed emotional profile and suggest music themes or specific song recommendations that would suit their mood.
    """

    # Get response from the LLM using Gemini
    try:
        llm_output = get_llm_response(prompt)
        return jsonify({
            "emotion": predicted_emotion,
            "detailed_emotion": llm_output
        })
    except Exception as e:
        return jsonify({"error": f"Failed to process LLM request: {str(e)}"}), 500