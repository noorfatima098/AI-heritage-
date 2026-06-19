import { useState } from "react";
import axios from "axios";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require("leaflet/dist/images/marker-icon-2x.png"),
  iconUrl:       require("leaflet/dist/images/marker-icon.png"),
  shadowUrl:     require("leaflet/dist/images/marker-shadow.png"),
});

export default function Identify() {
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
      const res = await axios.post("http://localhost:8000/identify", form);
      setResult(res.data);
    } catch {
      setError("Backend se connection nahi hua. FastAPI chal raha hai?");
    }
    setLoading(false);
  }

  return (
    <div style={s.page}>
      <div style={s.header}>
        <h1 style={s.title}>Identify a Landmark</h1>
        <p style={s.sub}>Upload a photo taken at Lahore Fort — our AI will recognise the monument and reveal its history.</p>
      </div>

      <div style={s.container}>
        {/* Upload */}
        <div style={s.card}>
          <label style={s.uploadBox}>
            {preview
              ? <img src={preview} alt="preview" style={s.preview} />
              : <div style={s.placeholder}>
                  <div style={s.uploadIcon}>📷</div>
                  <p style={s.uploadText}>Click to choose a photo</p>
                  <p style={s.uploadHint}>JPG, PNG supported</p>
                </div>
            }
            <input type="file" accept="image/*" onChange={handleFile} style={{ display:"none" }} />
          </label>
          <button onClick={handleSubmit} disabled={!image || loading} style={!image || loading ? s.btnOff : s.btn}>
            {loading ? "Identifying..." : "Identify Landmark"}
          </button>
          {error && <p style={s.error}>{error}</p>}
        </div>

        {/* Result */}
        {result && (
          <div style={s.results}>
            {!result.recognised
              ? <div style={s.notFound}>⚠️ {result.message}</div>
              : <>
                  <div style={s.card}>
                    <div style={s.topRow}>
                      <div>
                        <h2 style={s.name}>{result.name}</h2>
                        <p style={s.urdu}>{result.name_urdu}</p>
                        <p style={s.meta}>🏛 {result.built_by} · {result.year_built}</p>
                        <p style={s.meta}>🕌 {result.period} Period</p>
                        <p style={s.meta}>⭐ {result.significance}</p>
                      </div>
                      <div style={s.badge}>
                        <span style={s.badgeNum}>{result.confidence}%</span>
                        <span style={s.badgeLabel}>confidence</span>
                      </div>
                    </div>
                  </div>

                  <div style={s.card}>
                    <h3 style={s.sectionTitle}>📖 Historical Narrative</h3>
                    <p style={s.narrative}>{result.narrative}</p>
                  </div>

                  {result.coordinates && (
                    <div style={s.card}>
                      <h3 style={s.sectionTitle}>📍 Location on Map</h3>
                      <MapContainer center={[result.coordinates.lat, result.coordinates.lng]} zoom={17} style={{ height:280, borderRadius:6 }}>
                        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                        <Marker position={[result.coordinates.lat, result.coordinates.lng]}>
                          <Popup>{result.name}</Popup>
                        </Marker>
                      </MapContainer>
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

const s = {
  page:        { minHeight:"100vh", background:"#FAFAF8", fontFamily:"'Inter',sans-serif" },
  header:      { background:"#3D2314", padding:"48px", textAlign:"center" },
  title:       { fontFamily:"'Playfair Display',serif", color:"#FAFAF8", fontSize:36, fontWeight:700, marginBottom:12 },
  sub:         { color:"#C4A882", fontSize:15, fontWeight:300, maxWidth:560, margin:"0 auto" },
  container:   { maxWidth:800, margin:"0 auto", padding:"32px 24px", display:"flex", flexDirection:"column", gap:20 },
  card:        { background:"#fff", border:"1px solid #E8E4DC", borderRadius:8, padding:28 },
  uploadBox:   { display:"block", cursor:"pointer", border:"2px dashed #C4A882", borderRadius:6, overflow:"hidden", marginBottom:16 },
  placeholder: { padding:"48px 24px", textAlign:"center" },
  uploadIcon:  { fontSize:40, marginBottom:12 },
  uploadText:  { color:"#7B4F2E", fontSize:16, fontWeight:500 },
  uploadHint:  { color:"#8C8580", fontSize:13, marginTop:6 },
  preview:     { width:"100%", maxHeight:300, objectFit:"cover", display:"block" },
  btn:         { width:"100%", background:"#7B4F2E", color:"#FAFAF8", border:"none", padding:"14px", borderRadius:6, fontSize:15, fontWeight:500, cursor:"pointer", fontFamily:"'Inter',sans-serif" },
  btnOff:      { width:"100%", background:"#C4A882", color:"#fff", border:"none", padding:"14px", borderRadius:6, fontSize:15, fontFamily:"'Inter',sans-serif" },
  error:       { color:"#c0392b", marginTop:12, fontSize:14 },
  results:     { display:"flex", flexDirection:"column", gap:20 },
  notFound:    { background:"#fff8f0", border:"1px solid #e8c99a", borderRadius:8, padding:24, color:"#7B4F2E", fontWeight:500 },
  topRow:      { display:"flex", justifyContent:"space-between", alignItems:"flex-start", gap:16 },
  name:        { fontFamily:"'Playfair Display',serif", fontSize:26, color:"#3D2314", fontWeight:700, marginBottom:4 },
  urdu:        { fontSize:20, color:"#7B4F2E", marginBottom:12, fontFamily:"serif" },
  meta:        { color:"#6B6560", fontSize:13, marginBottom:6 },
  badge:       { background:"#EEEBE4", borderRadius:8, padding:"12px 20px", textAlign:"center", minWidth:90, flexShrink:0 },
  badgeNum:    { display:"block", fontFamily:"'Playfair Display',serif", fontSize:28, color:"#3D2314", fontWeight:700 },
  badgeLabel:  { display:"block", fontSize:11, color:"#8C8580", marginTop:2, textTransform:"uppercase", letterSpacing:1 },
  sectionTitle:{ fontFamily:"'Playfair Display',serif", fontSize:18, color:"#3D2314", marginBottom:14, fontWeight:600 },
  narrative:   { color:"#4A4747", lineHeight:1.85, fontSize:15 },
};