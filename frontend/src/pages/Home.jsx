import { useNavigate } from "react-router-dom";
import useReveal from "../hooks/useReveal";
import { Camera, Compass, MapPin, BookOpen } from "../components/Icon";
import "./Home.css";

const features = [
  { Icon: Camera,   title: "Snap & Identify",  desc: "Upload a photo taken anywhere inside the Fort and let AI recognise the monument in seconds." },
  { Icon: BookOpen, title: "Rich History",     desc: "Every landmark comes with a narrative on its Mughal, Sikh, or colonial-era significance." },
  { Icon: MapPin,   title: "Exact Location",   desc: "See precisely where you are standing, pinned on an interactive map of the Fort." },
  { Icon: Compass,  title: "Guided Discovery", desc: "Browse all eleven landmarks, search by name, and plan your own walking route." },
];

export default function Home() {
  const nav = useNavigate();
  const [featRef, featVisible] = useReveal();
  const [statRef, statVisible] = useReveal();

  return (
    <div className="page home-page">
      <section className="home-hero">
        <div className="home-arch" />
        <div className="home-hero-content">
          <p className="home-eyebrow">Lahore Fort · Mughal Heritage · AI-Powered</p>
          <h1 className="home-title">Discover the Walled<br />City of Lahore</h1>
          <p className="home-subtitle">
            Upload a photograph of any monument inside Lahore Fort and let AI
            reveal its history, architecture, and exact location on the map.
          </p>
          <div className="home-btn-row">
            <button className="btn btn-primary" onClick={() => nav("/identify")}>
              <Camera size={16} /> Identify a Landmark
            </button>
            <button className="btn btn-outline" onClick={() => nav("/explore")}>
              <Compass size={16} /> Explore Monuments
            </button>
            <button className="btn btn-outline" onClick={() => nav("/map")}>
              <MapPin size={16} /> View the Map
            </button>
          </div>
        </div>
      </section>

      <section ref={featRef} className={`home-features reveal ${featVisible ? "in-view" : ""}`}>
        {features.map(({ Icon, title, desc }, i) => (
          <div key={title} className="home-feature card card-hover" style={{ animationDelay: `${i * 60}ms` }}>
            <div className="home-feature-icon"><Icon size={22} /></div>
            <h3 className="home-feature-title">{title}</h3>
            <p className="home-feature-desc">{desc}</p>
          </div>
        ))}
      </section>

      <section ref={statRef} className={`home-stats reveal ${statVisible ? "in-view" : ""}`}>
        <div className="home-stat"><span className="home-stat-num">30+</span><span className="home-stat-label">Landmarks</span></div>
        <div className="home-stat"><span className="home-stat-num">1000s</span><span className="home-stat-label">Century-Old Structures</span></div>
        <div className="home-stat"><span className="home-stat-num">3</span><span className="home-stat-label">Historical Eras</span></div>
        <div className="home-stat"><span className="home-stat-num">AI</span><span className="home-stat-label">Powered Recognition</span></div>
      </section>
    </div>
  );
}
