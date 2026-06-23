import { useState, useEffect } from "react";
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

export default function Explore() {
  const [landmarks, setLandmarks] = useState([]);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    axios.get("http://localhost:8000/landmarks")
      .then(res => setLandmarks(res.data.landmarks))
      .catch(() => console.log("Backend se landmarks nahi mile"));
  }, []);

  return (
    <div style={s.page}>
      <div style={s.header}>
        <h1 style={s.title}>Explore Lahore Fort</h1>
        <p style={s.sub}>Click any marker on the map to learn about that landmark.</p>
      </div>

      <div style={s.body}>
        {/* Sidebar */}
        <div style={s.sidebar}>
          <p style={s.sideLabel}>All Landmarks</p>
          {landmarks.map(l => (
            <div
              key={l.id}
              style={{ ...s.sideItem, ...(selected?.id === l.id ? s.sideActive : {}) }}
              onClick={() => setSelected(l)}
            >
              <div style={s.sideName}>{l.name}</div>
              <div style={s.sideUrdu}>{l.name_urdu}</div>
              <div style={s.sideMeta}>{l.period} · {l.built_by}</div>
            </div>
          ))}
        </div>

        {/* Map */}
        <div style={s.mapWrap}>
          <MapContainer center={[31.5882, 74.3100]} zoom={16} style={{ height:"100%", width:"100%" }}>
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
            {landmarks.map(l => (
              <Marker key={l.id} position={[l.coordinates.lat, l.coordinates.lng]} eventHandlers={{ click: () => setSelected(l) }}>
                <Popup>
                  <strong>{l.name}</strong><br />
                  {l.name_urdu}<br />
                  <span style={{ color:"#7B4F2E", fontSize:12 }}>{l.built_by} · {l.period}</span>
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>
      </div>
    </div>
  );
}

const s = {
  page:       { minHeight:"100vh", background:"#FAFAF8", fontFamily:"'Inter',sans-serif" },
  header:     { background:"#3D2314", padding:"40px 48px", textAlign:"center" },
  title:      { fontFamily:"'Playfair Display',serif", color:"#FAFAF8", fontSize:34, fontWeight:700, marginBottom:10 },
  sub:        { color:"#C4A882", fontSize:15, fontWeight:300 },
  body:       { display:"grid", gridTemplateColumns:"300px 1fr", height:"calc(100vh - 180px)" },
  sidebar:    { overflowY:"auto", borderRight:"1px solid #E8E4DC", background:"#fff" },
  sideLabel:  { padding:"16px 20px 8px", fontSize:11, color:"#8C8580", textTransform:"uppercase", letterSpacing:2, fontWeight:500 },
  sideItem:   { padding:"14px 20px", borderBottom:"1px solid #F0EDE8", cursor:"pointer", transition:"background .15s" },
  sideActive: { background:"#EEEBE4", borderLeft:"3px solid #7B4F2E" },
  sideName:   { fontSize:14, fontWeight:500, color:"#3D2314", marginBottom:2 },
  sideUrdu:   { fontSize:13, color:"#7B4F2E", marginBottom:4 },
  sideMeta:   { fontSize:11, color:"#8C8580" },
  mapWrap:    { position:"relative" },
};