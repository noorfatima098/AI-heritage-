import { useState } from "react";
import axios from "axios";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { Camera, Sparkle, MapPin, BookOpen } from "../components/Icon";
import { SkeletonLine } from "../components/Skeleton";
import "./Identify.css";

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require("leaflet/dist/images/marker-icon-2x.png"),
  iconUrl:       require("leaflet/dist/images/marker-icon.png"),
  shadowUrl:     require("leaflet/dist/images/marker-shadow.png"),
});

export default function Identify() {
  const [enhancedUrl, setEnhancedUrl] = useState(null);
  const [enhancing, setEnhancing] = useState(false);
  const [image, setImage]     = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult]   = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);

  function handleFile(e) {
    const file = e.target.files[0];
    if (!file) return;
    setImage(file); setPreview(URL.createObjectURL(file));
    setResult(null); setError(null);
  }

  async function handleSubmit() {
    if (!image) return;
    setLoading(true); setError(null);
    try {
      const form = new FormData();
      form.append("file", image);

      // Best-effort GPS capture — if user denies permission or it times
      // out, we just skip it and identification falls back to CNN-only.
      const coords = await getLocation();
      if (coords) {
        form.append("lat", coords.lat);
        form.append("lng", coords.lng);
      }

      const res = await axios.post("http://localhost:8000/identify", form);
      setResult(res.data);
    } catch {
      setError("Backend se connection nahi hua. FastAPI chal raha hai?");
    }
    setLoading(false);
  }

  function getLocation() {
    return new Promise((resolve) => {
      if (!navigator.geolocation) return resolve(null);
      navigator.geolocation.getCurrentPosition(
        (pos) => resolve({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
        () => resolve(null),           // denied / unavailable — proceed without it
        { timeout: 5000, maximumAge: 60000 }
      );
    });
  }

  async function handleRevive() {
    if (!image) return;
    setEnhancing(true);
    try {
      const form = new FormData();
      form.append("file", image);
      const res = await axios.post("http://localhost:8000/enhance", form, {
        responseType: "blob"
      });
      const url = URL.createObjectURL(res.data);
      setEnhancedUrl(url);
    } catch {
      setError("Enhance fail ho gaya. Backend check karo.");
    }
    setEnhancing(false);
  }

  return (
    <div className="page identify-page">
      <div className="page-header">
        <h1 className="page-title">Identify a Landmark</h1>
        <p className="page-sub">Upload a photo taken at Lahore Fort — our AI will recognise the monument and reveal its history.</p>
      </div>

      <div className="identify-container">
        <div className="card identify-upload-card">
          <label className="identify-upload-box">
            {preview
              ? <img src={preview} alt="preview" className="identify-preview" />
              : <div className="identify-placeholder">
                  <div className="identify-upload-icon"><Camera size={30} /></div>
                  <p className="identify-upload-text">Click to choose a photo</p>
                  <p className="identify-upload-hint">JPG, PNG supported</p>
                </div>
            }
            <input type="file" accept="image/*" onChange={handleFile} style={{ display: "none" }} />
          </label>
          <button
            onClick={handleSubmit}
            disabled={!image || loading}
            className={`btn btn-block ${!image || loading ? "btn-ghost" : "btn-solid"}`}
          >
            {loading ? (<><span className="spinner" /> Identifying…</>) : "Identify Landmark"}
          </button>
          {error && <p className="identify-error">{error}</p>}
        </div>

        {loading && !result && (
          <div className="identify-results">
            <div className="card identify-card">
              <SkeletonLine width="55%" height={26} />
              <div style={{ height: 10 }} />
              <SkeletonLine width="35%" height={14} />
              <div style={{ height: 8 }} />
              <SkeletonLine width="70%" height={14} />
            </div>
          </div>
        )}

        {result && (
          <div className="identify-results">
            {!result.recognised
              ? <div className="identify-notfound">⚠️ {result.message}</div>
              : <>
                  <div className="card identify-card identify-top">
                    <div>
                      <h2 className="identify-name">{result.name}</h2>
                      <p className="identify-urdu">{result.name_urdu}</p>
                      <p className="identify-meta"><Sparkle size={13} /> {result.built_by} · {result.year_built}</p>
                      <p className="identify-meta"><BookOpen size={13} /> {result.period} Period</p>
                      <p className="identify-meta">⭐ {result.significance}</p>
                    </div>
                    <div className="identify-badge">
                      <span className="identify-badge-num">{result.confidence}%</span>
                      <span className="identify-badge-label">confidence</span>
                    </div>
                  </div>

                  <div className="card identify-card">
                    <h3 className="identify-section-title"><BookOpen size={16} /> Historical Narrative</h3>
                    <p className="identify-narrative">{result.narrative}</p>
                  </div>

                  <div className="card identify-card">
                    <h3 className="identify-section-title"><Sparkle size={16} /> Revive Photo</h3>
                    <button onClick={handleRevive} disabled={enhancing} className="btn btn-solid">
                      {enhancing ? (<><span className="spinner" /> Reviving…</>) : "Revive This Photo"}
                    </button>
                    {enhancedUrl && (
                      <img src={enhancedUrl} alt="enhanced" className="identify-enhanced" />
                    )}
                  </div>

                  {result.coordinates && (
                    <div className="card identify-card">
                      <h3 className="identify-section-title"><MapPin size={16} /> Location on Map</h3>
                      <div className="identify-map">
                        <MapContainer center={[result.coordinates.lat, result.coordinates.lng]} zoom={17} style={{ height: "100%" }}>
                          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                          <Marker position={[result.coordinates.lat, result.coordinates.lng]}>
                            <Popup>{result.name}</Popup>
                          </Marker>
                        </MapContainer>
                      </div>
                    </div>
                  )}
                </>
            }
          </div>
        )}
      </div>
    </div>
  );
}