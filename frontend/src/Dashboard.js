import React, { useState, useCallback, useRef } from 'react';
import Webcam from 'react-webcam';

const Dashboard = () => {
  const [emotion, setEmotion] = useState('');
  const [detailedEmotion, setDetailedEmotion] = useState('');
  const [artist, setArtist] = useState('');
  const [language, setLanguage] = useState('');
  const [image, setImage] = useState(null);
  const [error, setError] = useState('');

  const webcamRef = useRef(null);

  const capture = useCallback(() => {
    const imageSrc = webcamRef.current.getScreenshot();
    setImage(imageSrc);
    if (!imageSrc) {
      setError('No image captured. Please try again.');
    } else {
      setError('');
    }
  }, [webcamRef]);

  const dataURLtoFile = (dataurl, filename) => {
    const arr = dataurl.split(',');
    const mime = arr[0].match(/:(.*?);/)[1];
    const bstr = atob(arr[1]);
    let n = bstr.length;
    const u8arr = new Uint8Array(n);
    while (n--) {
      u8arr[n] = bstr.charCodeAt(n);
    }
    return new File([u8arr], filename, { type: mime });
  };

  const handleSend = async () => {
    if (!image || !artist || !language) {
      setError('Please provide an image, artist, and language preference!');
      return;
    }

    setError('');  // Clear any previous errors

    try {
      const formData = new FormData();
      const imageFile = dataURLtoFile(image, 'emotion-image.jpg');
      formData.append('image', imageFile);
      formData.append('artist', artist);
      formData.append('language', language);

      const response = await fetch('http://127.0.0.1:5000/emotion/detect_emotion', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setEmotion(data.emotion);  // Basic emotion detected by the model
      setDetailedEmotion(data.detailed_emotion);  // Detailed emotional profile from the LLM
    } catch (error) {
      console.error('Error:', error);
      setError(`Error: ${error.message}. Please ensure the backend server is running.`);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    window.location.href = '/login';
  };

  // Helper function to format LLM output into structured HTML
  const renderDetailedEmotion = () => {
    if (!detailedEmotion) return null;

    // Split the text into sections based on the LLM output
    const sections = detailedEmotion.split('*');

    return (
      <div className="emotion-profile">
        {sections.map((section, index) => (
          <p key={index}>{section.trim()}</p>
        ))}
      </div>
    );
  };

  return (
    <div className="dashboard-container">
      <button className="logout-button" onClick={handleLogout}>Logout</button>

      <h1>Music Recommendation Dashboard</h1>

      <div className="webcam-container">
        {!image && (
          <>
            <Webcam
              audio={false}
              ref={webcamRef}
              screenshotFormat="image/jpeg"
            />
            <button onClick={capture}>Capture Emotion</button>
          </>
        )}
      </div>

      {image && (
        <div className="image-preview">
          <img src={image} alt="Captured emotion" />
          <button onClick={() => setImage(null)}>Retake Photo</button>
        </div>
      )}

      <div className="input-section">
        <label>Favorite Artist:</label>
        <input
          type="text"
          value={artist}
          onChange={(e) => setArtist(e.target.value)}
          placeholder="Enter your favorite artist"
        />
      </div>

      <div className="input-section">
        <label>Preferred Language:</label>
        <input
          type="text"
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          placeholder="Enter your preferred language"
        />
      </div>

      <button onClick={handleSend}>Submit</button>

      {error && <p className="error-message" style={{ color: 'red' }}>{error}</p>}

      {emotion && (
        <div className="results-section">
          <h2>Detected Emotion: {emotion}</h2>
          <h3>Detailed Emotional Profile:</h3>
          {renderDetailedEmotion()}
        </div>
      )}
    </div>
  );
};

export default Dashboard;
