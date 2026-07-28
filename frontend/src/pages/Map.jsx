import { useState, useEffect } from "react";
import axios from "axios";
import { useLocation } from "react-router-dom";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { MapPin } from "../components/Icon";
import "./Map.css";

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require("leaflet/dist/images/marker-icon-2x.png"),
  iconUrl:       require("leaflet/dist/images/marker-icon.png"),
  shadowUrl:     require("leaflet/dist/images/marker-shadow.png"),
});

export default function Map() {
  const [landmarks, setLandmarks] = useState([]);
  const [selected, setSelected]   = useState(null);
  const [loading, setLoading]     = useState(true);
  const location = useLocation();

  useEffect(() => {
    axios.get("http://localhost:8000/landmarks")
      .then(res => {
        const list = res.data.landmarks || [];
        setLandmarks(list);
        const focusId = new URLSearchParams(location.search).get("focus");
        if (focusId) setSelected(list.find(l => l.id === focusId) || null);
      })
      .catch(() => console.log("Backend se landmarks nahi mile"))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="page map-page">
      <div className="page-header">
        <h1 className="page-title">Explore Lahore Fort</h1>
        <p className="page-sub">Click any marker on the map to learn about that landmark.</p>
      </div>

      <div className="map-body">
        <div className="map-sidebar">
          <p className="map-side-label">All Landmarks</p>
          {loading ? (
            <div className="map-side-loading">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="skeleton" style={{ height: 58, margin: "0 20px 10px", borderRadius: 8 }} />
              ))}
            </div>
          ) : (
            landmarks.map(l => (
              <div
                key={l.id}
                className={`map-side-item${selected?.id === l.id ? " active" : ""}`}
                onClick={() => setSelected(l)}
              >
                <div className="map-side-name">{l.name}</div>
                <div className="map-side-urdu">{l.name_urdu}</div>
                <div className="map-side-meta">{l.period} · {l.built_by}</div>
              </div>
            ))
          )}
        </div>

        <div className="map-canvas">
          <MapContainer center={[31.5882, 74.3100]} zoom={16} style={{ height: "100%", width: "100%" }}>
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
            {landmarks.map(l => (
              <Marker
                key={l.id}
                position={[l.coordinates.lat, l.coordinates.lng]}
                eventHandlers={{ click: () => setSelected(l) }}
              >
                <Popup>
                  <strong>{l.name}</strong><br />
                  {l.name_urdu}<br />
                  <span style={{ color: "#7B4F2E", fontSize: 12, display: "inline-flex", alignItems: "center", gap: 4, marginTop: 4 }}>
                    <MapPin size={12} /> {l.built_by} · {l.period}
                  </span>
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>
      </div>
    </div>
  );
}
