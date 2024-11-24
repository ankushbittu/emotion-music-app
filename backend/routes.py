import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from flask_cors import CORS
from models import User
from extensions import db
from tensorflow.keras.models import load_model
import numpy as np
import cv2
import logging
from flask_jwt_extended import create_access_token
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

# Setting up blueprint and logging
main = Blueprint('main', __name__)
CORS(main)
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

# Load Gemini and Spotify credentials
gemini_api_key = os.getenv('GEMINI_API_KEY')
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

# Configure Gemini API
genai.configure(api_key=gemini_api_key)

# Configure Spotify OAuth
sp_oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="playlist-modify-public"
)

# Load the trained CNN model
model_path = "C:/Users/HP BITTU/Downloads/emotion_basic.keras"
model = load_model(model_path)

# Load Haar Cascade for face detection
face_cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(face_cascade_path)

# Define emotion labels
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

# Helper function to call Gemini API
def get_llm_response(prompt):
    try:
        model = genai.GenerativeModel('gemini-pro')
        chat = model.start_chat(history=[])
        response = chat.send_message(prompt)
        logging.debug(f"LLM Response: {response.text}")
        return response.text.strip()
    except Exception as e:
        logging.error(f"Error calling LLM API: {e}")
        return None

# Helper function for Spotify API
def get_spotify_client():
    token_info = sp_oauth.get_cached_token()
    if not token_info:
        token_info = sp_oauth.get_access_token(as_dict=True)
    return Spotify(auth=token_info['access_token'])

@main.route('/emotion/detect_emotion', methods=['POST'])
def detect_emotion():
    data = request.form
    image_file = request.files.get('image')

    if not image_file or not data.get('artist') or not data.get('language'):
        return jsonify({"error": "Missing image, artist, or language"}), 400

    try:
        # Preprocess image
        image_bytes = image_file.read()
        image_array = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) == 0:
            return jsonify({"error": "No face detected in the image"}), 400

        x, y, w, h = faces[0]
        face = gray_image[y:y + h, x:x + w]
        resized_face = cv2.resize(face, (48, 48))
        normalized_face = resized_face / 255.0
        face_array = np.expand_dims(normalized_face, axis=(0, -1))
        predictions = model.predict(face_array)
        predicted_emotion = emotion_labels[np.argmax(predictions)]

        # Generate prompt for LLM
        
        artist = data.get('artist')
        language = data.get('language')
        prompt = f"""
            The user is feeling {predicted_emotion}, and they prefer songs by the artist "{artist}". The recommendations should primarily include songs by "{artist}" that align with this emotion and are available in "{language}".

            If there aren’t enough songs by "{artist}" that match, include tracks from similar artists in "{language}" who resonate with the "{predicted_emotion}" mood.

            Provide a structured list of at least 15 songs:
            1. Start with tracks by "{artist}" that align with the "{predicted_emotion}" mood.
            2. If necessary, add similar songs from related artists and briefly explain their connection to the mood and genre.
            3. Ensure the songs are listed in the format: "Song Title - Artist Name".

            For example:
            1. "Blinding Lights - The Weeknd" (Mood: Happy, Genre: Synthwave)
            2. "Can't Feel My Face - The Weeknd" (Mood: Playful, Genre: Pop)
            ...
            """
        llm_output = get_llm_response(prompt)
        if not llm_output:
            return jsonify({"error": "Failed to get response from LLM"}), 500

        # Extract songs from LLM response
        song_recommendations = [song.strip() for song in llm_output.split("\n") if song]

        # Create Spotify playlist
        spotify = get_spotify_client()
        user_id = spotify.me()['id']
        playlist = spotify.user_playlist_create(
            user_id, f"{predicted_emotion.capitalize()} Mood Playlist", public=True
        )
        playlist_id = playlist['id']

        # Add songs to playlist
        track_ids = []
        for song in song_recommendations:
            search_results = spotify.search(q=song, type='track', limit=1)
            if search_results['tracks']['items']:
                track_ids.append(search_results['tracks']['items'][0]['uri'])

        if track_ids:
            spotify.playlist_add_items(playlist_id, track_ids)

        return jsonify({
            "success": True,
            "emotion_detected": predicted_emotion,
            "detailed_emotion": llm_output,
            "playlist_url": playlist['external_urls']['spotify']
        })

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({"error": str(e)}), 500
