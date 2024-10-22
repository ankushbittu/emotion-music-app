import React, { useState } from 'react';
import Webcam from 'react-webcam';

const Dashboard = () => {
  const [emotion, setEmotion] = useState('');  // Emotion detected by the CNN
  const [artist, setArtist] = useState('');
  const [language, setLanguage] = useState('');
  const [playlistLink, setPlaylistLink] = useState('');
  const [image, setImage] = useState(null); // Store captured image

  const webcamRef = React.useRef(null);

  const capture = React.useCallback(() => {
    const imageSrc = webcamRef.current.getScreenshot();
    setImage(imageSrc);
  }, [webcamRef]);

  const handleSend = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/detect-emotion', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image: image,  // Send captured image to backend for emotion detection
          artist: artist,
          language: language,
        }),
      });

      const data = await response.json();
      setEmotion(data.emotion);  // Get detected emotion from backend
      setPlaylistLink(data.playlistLink);  // Get playlist link from backend
    } catch (error) {
      console.error('Error fetching emotion:', error);
    }
  };

  return (
    <div className="dashboard-container">
      <button className="logout-button" onClick={() => { localStorage.removeItem('token'); window.location.href = '/login'; }}>Logout</button>

      <h1>Music Recommendation Dashboard</h1>

      {/* Webcam Capture */}
      <div className="webcam-container">
        <Webcam
          audio={false}
          ref={webcamRef}
          screenshotFormat="image/jpeg"
        />
        <button onClick={capture}>Capture Emotion</button>
      </div>

      {/* Display captured image */}
      {image && <img src={image} alt="captured emotion" />}

      {/* Display detected emotion */}
      {emotion && <h2>Detected Emotion: {emotion}</h2>}

      {/* Artist and Language Input */}
      <div className="input-section">
        <label>Artist:</label>
        <input type="text" value={artist} onChange={(e) => setArtist(e.target.value)} placeholder="Enter favorite artist" />
      </div>
      <div className="input-section">
        <label>Language:</label>
        <input type="text" value={language} onChange={(e) => setLanguage(e.target.value)} placeholder="Enter preferred language" />
      </div>

      {/* Send Data to Backend */}
      <button onClick={handleSend}>Send</button>

      {/* Playlist Link */}
      {playlistLink && (
        <div className="playlist-section">
          <h3>Your Playlist:</h3>
          <a href={playlistLink} target="_blank" rel="noopener noreferrer">Listen to your playlist</a>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
