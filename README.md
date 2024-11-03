Emotion-Driven Music Recommendation System
This project is an intelligent music recommendation system that leverages facial emotion recognition and large language models (LLMs) to enhance the personalization of music recommendations. It captures real-time emotions through a camera, analyzes them using a Convolutional Neural Network (CNN), and suggests music tracks that match the detected emotion using the Spotify API.

Table of Contents
Features
Technologies Used
Project Architecture
Installation
Usage
Future Improvements
License
Features
Real-time Emotion Detection: Recognizes facial emotions using a CNN model trained on the FER 2013 dataset with 69% accuracy.
Music Recommendation via Spotify API: Provides music suggestions that align with the detected emotion.
Integration with LLMs: Generates nuanced emotion analysis and personalized recommendations, enhancing user engagement.
React and Flask Dashboard: Interactive frontend interface for capturing images, displaying detected emotions, and offering music suggestions.
Technologies Used
Frontend: React.js
Backend: Flask
Machine Learning: TensorFlow/Keras for CNN model, LLMs for nuanced emotion analysis
API Integration: Spotify API for music recommendations
Cloud Deployment: (Specify cloud provider, e.g., AWS, Azure, etc., if used)
Project Architecture
css
Copy code
Emotion-Driven Music Recommendation System
│
├── frontend/
│   └── src/
│       └── App.js
│       └── components/
│           └── CameraCapture.js
│           └── EmotionDisplay.js
│           └── MusicRecommendation.js
│
├── backend/
│   ├── app.py
│   └── model/
│       └── final_model.keras
│
├── README.md
└── requirements.txt
Frontend: React app for the user interface, which includes image capture, emotion display, and music recommendation components.
Backend: Flask server for handling model inference, emotion detection, and Spotify API integration.
Model: Pre-trained CNN model (final_model.keras) used for emotion detection.
Installation
Clone the Repository

bash
Copy code
git clone https://github.com/yourusername/emotion-music-app.git
cd emotion-music-app
Install Backend Dependencies

bash
Copy code
cd backend
pip install -r requirements.txt
Install Frontend Dependencies

bash
Copy code
cd ../frontend
npm install
Set Up Spotify API Credentials

Create a Spotify developer account here and set up a new app to obtain CLIENT_ID and CLIENT_SECRET.
Add these credentials to the Flask backend environment.
Start the Backend

bash
Copy code
cd backend
python app.py
Start the Frontend

bash
Copy code
cd ../frontend
npm start
Access the Application

Open http://localhost:3001 in your browser to start using the app.
Usage
Capture Emotion: The dashboard displays a live camera feed. Capture an image to detect the current emotion.
Analyze Emotion: The CNN model processes the captured image and displays the detected emotion (e.g., happy, sad).
Get Music Recommendation: Based on the emotion, the app fetches a playlist from Spotify that matches the detected mood.
Future Improvements
Improved Emotion Detection Accuracy: Implement advanced transfer learning techniques for higher accuracy.
Expanded Music Options: Offer genre and language customization for music suggestions.
Enhanced LLM Integration: Improve emotion analysis to provide richer, context-aware recommendations.
License
This project is licensed under the MIT License. See the LICENSE file for more information.

