import { useState, useEffect, useRef } from "react";
import axios from "axios";
import "./AR.css";

const DEMO_LANDMARKS = [
  { id: "sheesh-mahal", name: "Sheesh Mahal", lat: 31.589957477792083, lng: 74.31318332623091 },
  { id: "picture-wall", name: "Picture Wall", lat: 31.589706154227873, lng: 74.31288090707392 },
  { id: "alamgiri-gate", name: "Alamgiri Gate", lat: 31.588531237106725, lng: 74.31269642617329 },
  { id: "hathi-peer-stairs", name: "Hathi Peer Stairs", lat: 31.589470825257315, lng: 74.31285242755285 },
  { id: "athdara", name: "Athdara", lat: 31.589756321435324, lng: 74.31344648329733 },
  { id: "diwan-i-amm", name: "Diwan-i-Aam", lat: 31.58812973444832, lng: 74.31529077192928 },
  { id: "moti-masjid", name: "Moti Masjid", lat: 31.588441112458856, lng: 74.31369913832265 },
  { id: "shahi-hammam", name: "Shahi Hammam", lat: 31.58905513778987, lng: 74.3140871027145 },
  { id: "jahangir-quadrangle", name: "Jahangir's Quadrangle", lat: 31.588891246492974, lng: 74.31558775081817 },
  { id: "lal-burj", name: "Lal Burj", lat: 31.58959549528335, lng: 74.31439846540577 },
  { id: "naulakha-pavilion", name: "Naulakha Pavilion", lat: 31.5898021142141, lng: 74.31292985740865 },
  { id: "kala-burj", name: "Kala Burj", lat: 31.589748467606846, lng: 74.31387005320975 },
  { id: "pain-bagh", name: "Pain Bagh", lat: 31.589281846202603, lng: 74.3140728911412 },
  { id: "barood-khana", name: "Barood Khana", lat: 31.588805527777772, lng: 74.31276666666665 },
  { id: "maktab-khana", name: "Maktab Khana", lat: 31.58838842296839, lng: 74.31395407816925 },
  { id: "shah-jahan-quadrangle", name: "Shah Jahan Quadrangle", lat: 31.589233330643992, lng: 74.31465963109176 },
  { id: "doulat-khana", name: "Daulat Khana", lat: 31.588277103981138, lng: 74.3153256406436 },
  { id: "haveli-mai-jindan", name: "Haveli Mai Jindan", lat: 31.58862557277238, lng: 74.31473222505946 },
  { id: "khwabgah-jahangir", name: "Khwabgah-i-Jahangiri", lat: 31.58928938849217, lng: 74.31567868426711 },
  { id: "british-jail", name: "British Jail", lat: 31.589386083333338, lng: 74.31343888888887 },
  { id: "shah-burj-gate", name: "Shah Burj Gate", lat: 31.589311916399346, lng: 74.31274695934556 },
  { id: "royal-kitchen", name: "Royal Kitchen", lat: 31.58797074328574, lng: 74.31302990994524 },
  { id: "loh-temple", name: "Loh Temple", lat: 31.58817427684184, lng: 74.31283352489811 },
  { id: "akbari-gate", name: "Masti Gate", lat: 31.587521851166674, lng: 74.31679914517618 },
  { id: "sikh-wall", name: "Sikh Wall", lat: 31.59001568002496, lng: 74.31566079706975 },
  { id: "stables", name: "Royal Stables", lat: 31.588291953708055, lng: 74.31695248320518 },
  { id: "akbari-mahal-kutab-khana", name: "Akbari Mahal Kutab Khana", lat: 31.588435046951975, lng: 74.31591874566337 },
  { id: "akbari-hammam", name: "Akbari Hammam", lat: 31.588435322023113, lng: 74.31665750885824 },
];

export default function AR() {
  const videoRef = useRef(null);
  const [demoMode, setDemoMode] = useState(false);
  const [selectedLandmark, setSelectedLandmark] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [cameraOn, setCameraOn] = useState(false);
  const [error, setError] = useState(null);

  // Camera start karo
  async function startCamera() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment" } // back camera
      });
      videoRef.current.srcObject = stream;
      setCameraOn(true);
      setError(null);
    } catch {
      setError("Camera access nahi mila. Browser permissions check karo.");
    }
  }

  function stopCamera() {
    const stream = videoRef.current?.srcObject;
    if (stream) stream.getTracks().forEach(t => t.stop());
    setCameraOn(false);
    setResult(null);
  }

  // Demo mode — manually landmark select karo
async function handleDemoSelect(landmark) {
  setSelectedLandmark(landmark);
  setLoading(true);
  setResult(null);
  try {
    const res = await axios.get(
      `http://localhost:8000/identify-by-gps?lat=${landmark.lat}&lng=${landmark.lng}`
    );
    setResult(res.data);
  } catch {
    setResult({ name: landmark.name, confidence: 99.0, identified_by: "Demo" });
  }
  setLoading(false);
}

  return (
    <div className="ar-page">
      {/* Header */}
      <div className="ar-header">
        <h1 className="ar-title">AR Heritage View</h1>
        <p className="ar-sub">Point your camera at any Lahore Fort monument</p>
      </div>

      {/* Camera View */}
      <div className="ar-viewport">
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className="ar-video"
        />

        {/* AR Overlay — result dikhao */}
        {result && (
          <div className="ar-overlay">
            <div className="ar-overlay-card">
              <div className="ar-overlay-badge">
                {result.identified_by === "Demo GPS" ? "📍 Demo" : "📍 GPS"}
              </div>
              <h2 className="ar-overlay-name">{result.name}</h2>
              {result.name_urdu && (
                <p className="ar-overlay-urdu">{result.name_urdu}</p>
              )}
              {result.period && (
                <p className="ar-overlay-meta">{result.built_by} · {result.year_built}</p>
              )}
              {result.narrative && (
                <p className="ar-overlay-narrative">{result.narrative}</p>
              )}
              <div className="ar-overlay-confidence">
                {result.confidence}% match
              </div>
            </div>
          </div>
        )}

        {/* Camera off state */}
        {!cameraOn && (
          <div className="ar-camera-placeholder">
            <div className="ar-camera-icon">📷</div>
            <p>Camera band hai</p>
          </div>
        )}

        {loading && (
          <div className="ar-loading">
            <div className="ar-spinner" />
            <p>Identifying...</p>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="ar-controls">
        {!cameraOn ? (
          <button className="ar-btn ar-btn-primary" onClick={startCamera}>
            📷 Start Camera
          </button>
        ) : (
          <button className="ar-btn ar-btn-danger" onClick={stopCamera}>
            ⏹ Stop Camera
          </button>
        )}

        <button
          className={`ar-btn ${demoMode ? "ar-btn-active" : "ar-btn-secondary"}`}
          onClick={() => { setDemoMode(!demoMode); setResult(null); }}
        >
          🎭 {demoMode ? "Demo Mode ON" : "Demo Mode"}
        </button>
      </div>

      {/* Demo Mode — landmark select */}
      {demoMode && (
        <div className="ar-demo-panel">
          <p className="ar-demo-label">Select a landmark to simulate:</p>
          <div className="ar-demo-grid">
            {DEMO_LANDMARKS.map(l => (
              <button
                key={l.id}
                className={`ar-demo-item ${selectedLandmark?.id === l.id ? "ar-demo-active" : ""}`}
                onClick={() => handleDemoSelect(l)}
              >
                {l.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {error && <p className="ar-error">{error}</p>}
    </div>
  );
}