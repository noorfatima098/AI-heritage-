import { useState } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require("leaflet/dist/images/marker-icon-2x.png"),
  iconUrl:       require("leaflet/dist/images/marker-icon.png"),
  shadowUrl:     require("leaflet/dist/images/marker-shadow.png"),
});

const landmarks = [
  { id:"sheesh-mahal",         name:"Sheesh Mahal",          urdu:"شیش محل",      lat:31.5883, lng:74.3101, period:"Mughal", built:"Shah Jahan" },
  { id:"alamgiri-gate",        name:"Alamgiri Gate",         urdu:"عالمگیری دروازہ", lat:31.5882, lng:74.3088, period:"Mughal", built:"Aurangzeb" },
  { id:"picture-wall",         name:"Picture Wall",          urdu:"تصویری دیوار", lat:31.5888, lng:74.3101, period:"Mughal", built:"Jahangir" },
  { id:"diwan-i-amm",          name:"Diwan-i-Aam",           urdu:"دیوان عام",    lat:31.5879, lng:74.3103, period:"Mughal", built:"Shah Jahan" },
  { id:"naulakha-pavilion",    name:"Naulakha Pavilion",     urdu:"نولکھا",       lat:31.5886, lng:74.3104, period:"Mughal", built:"Shah Jahan" },
  { id:"moti-masjid",          name:"Moti Masjid",           urdu:"موتی مسجد",    lat:31.5878, lng:74.3097, period:"Mughal", built:"Shah Jahan" },
  { id:"hazuri-bagh",          name:"Hazuri Bagh",           urdu:"حضوری باغ",    lat:31.5877, lng:74.3093, period:"Sikh",   built:"Ranjit Singh" },
  { id:"hathi-paer-stairs",    name:"Hathi Paer",            urdu:"ہاتھی پیر",    lat:31.5881, lng:74.3092, period:"Mughal", built:"Akbar" },
  { id:"maktab-khana",         name:"Maktab Khana",          urdu:"مکتب خانہ",    lat:31.5887, lng:74.3098, period:"Mughal", built:"Mughal" },
  { id:"shah-jahan-quadrangle",name:"Shah Jahan Quadrangle", urdu:"شاہ جہاں صحن", lat:31.5882, lng:74.3105, period:"Mughal", built:"Shah Jahan" },
  { id:"imperial-kitchens",    name:"Imperial Kitchens",     urdu:"شاہی باورچی خانہ", lat:31.5876, lng:74.3098, period:"Mughal", built:"Mughal" },
];

export default function Explore() {
  const [selected, setSelected] = useState(null);

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
              <div style={s.sideUrdu}>{l.urdu}</div>
              <div style={s.sideMeta}>{l.period} · {l.built}</div>
            </div>
          ))}
        </div>

        {/* Map */}
        <div style={s.mapWrap}>
          <MapContainer center={[31.5882, 74.3100]} zoom={16} style={{ height:"100%", width:"100%" }}>
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
            {landmarks.map(l => (
              <Marker key={l.id} position={[l.lat, l.lng]} eventHandlers={{ click: () => setSelected(l) }}>
                <Popup>
                  <strong>{l.name}</strong><br />
                  {l.urdu}<br />
                  <span style={{ color:"#7B4F2E", fontSize:12 }}>{l.built} · {l.period}</span>
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