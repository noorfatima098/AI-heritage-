import { useState } from "react";
import axios from "axios";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

// Fix default marker icon
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require("leaflet/dist/images/marker-icon-2x.png"),
  iconUrl: require("leaflet/dist/images/marker-icon.png"),
  shadowUrl: require("leaflet/dist/images/marker-shadow.png"),
});

export default function App() {
  const [image, setImage]       = useState(null);
  const [preview, setPreview]   = useState(null);
  const [result, setResult]     = useState(null);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState(null);

  function handleFile(e) {
    const file = e.target.files[0];
    if (!file) return;
    setImage(file);
    setPreview(URL.createObjectURL(file));
    setResult(null);
    setError(null);
  }

  async function handleSubmit() {
    if (!image) return;
    setLoading(true);
    setError(null);
    try {
      const form = new FormData();
      form.append("file", image);
      const res = await axios.post("http://localhost:8000/identify", form);
      setResult(res.data);
    } catch (err) {
      setError("connection error");
    }
    setLoading(false);
  }

  return (
    <div style={styles.page}>

      {/* Header */}
      <div style={styles.header}>
        <h1 style={styles.title}>AI Heritage Revive</h1>
        <p style={styles.subtitle}>Walled City of Lahore</p>
      </div>

      {/* Upload Section */}
      <div style={styles.card}>
        <p style={styles.label}>upload picture of Lahore Fort.</p>
        <input type="file" accept="image/*" onChange={handleFile} style={styles.input} />

        {preview && (
          <img src={preview} alt="preview" style={styles.preview} />
        )}

        <button
          onClick={handleSubmit}
          disabled={!image || loading}
          style={loading ? styles.btnDisabled : styles.btn}
        >
          {loading ? "loading......" : "execute"}
        </button>

        {error && <p style={styles.error}>{error}</p>}
      </div>

      {/* Result Section */}
      {result && (
        <div>
          {result.recognised === false ? (
            <div style={styles.card}>
              <p style={styles.notFound}>⚠️ {result.message}</p>
            </div>
          ) : (
            <>
              {/* Name + Confidence */}
              <div style={styles.card}>
                <div style={styles.row}>
                  <div>
                    <h2 style={styles.monumentName}>{result.name}</h2>
                    <p style={styles.urdu}>{result.name_urdu}</p>
                    <p style={styles.meta}>🏛 {result.built_by} · {result.year_built} · {result.period}</p>
                    <p style={styles.meta}>⭐ {result.significance}</p>
                  </div>
                  <div style={styles.badge}>
                    {result.confidence}%
                    <span style={styles.badgeLabel}>confidence</span>
                  </div>
                </div>
              </div>

              {/* Narrative */}
              <div style={styles.card}>
                <h3 style={styles.sectionTitle}>📖 History</h3>
                <p style={styles.narrative}>{result.narrative}</p>
              </div>

              {/* Map */}
              {result.coordinates && (
                <div style={styles.card}>
                  <h3 style={styles.sectionTitle}>📍 Location</h3>
                  <MapContainer
                    center={[result.coordinates.lat, result.coordinates.lng]}
                    zoom={17}
                    style={{ height: "300px", borderRadius: "10px" }}
                  >
                    <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                    <Marker position={[result.coordinates.lat, result.coordinates.lng]}>
                      <Popup>{result.name}</Popup>
                    </Marker>
                  </MapContainer>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}

const styles = {
  page:          { maxWidth: 700, margin: "0 auto", padding: "20px", fontFamily: "Arial, sans-serif", background: "#f5f3ee", minHeight: "100vh" },
  header:        { textAlign: "center", padding: "30px 0 10px" },
  title:         { fontSize: 28, fontWeight: "bold", color: "#1a1a1a", margin: 0 },
  subtitle:      { color: "#534AB7", fontSize: 16, marginTop: 4 },
  card:          { background: "#fff", borderRadius: 12, padding: 20, marginBottom: 16, boxShadow: "0 2px 8px rgba(0,0,0,0.08)" },
  label:         { color: "#555", marginBottom: 12 },
  input:         { display: "block", marginBottom: 16 },
  preview:       { width: "100%", maxHeight: 280, objectFit: "cover", borderRadius: 8, marginBottom: 16 },
  btn:           { background: "#534AB7", color: "#fff", border: "none", padding: "12px 32px", borderRadius: 8, fontSize: 16, cursor: "pointer", width: "100%" },
  btnDisabled:   { background: "#aaa", color: "#fff", border: "none", padding: "12px 32px", borderRadius: 8, fontSize: 16, width: "100%" },
  error:         { color: "red", marginTop: 10 },
  notFound:      { color: "#c85000", fontWeight: "bold" },
  row:           { display: "flex", justifyContent: "space-between", alignItems: "flex-start" },
  monumentName:  { fontSize: 24, fontWeight: "bold", color: "#1a1a1a", margin: "0 0 4px" },
  urdu:          { fontSize: 20, color: "#534AB7", margin: "0 0 8px", fontFamily: "serif" },
  meta:          { color: "#666", fontSize: 14, margin: "4px 0" },
  badge:         { background: "#E1F5EE", color: "#085041", borderRadius: 10, padding: "8px 16px", textAlign: "center", fontWeight: "bold", fontSize: 22, display: "flex", flexDirection: "column", minWidth: 80 },
  badgeLabel:    { fontSize: 11, fontWeight: "normal", marginTop: 2 },
  sectionTitle:  { fontWeight: "bold", marginBottom: 12, color: "#1a1a1a" },
  narrative:     { color: "#333", lineHeight: 1.8, fontSize: 15 },
};
//npm start