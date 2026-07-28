import useReveal from "../hooks/useReveal";
import "./About.css";

const techStack = [
  { label: "Image Classification", value: "Google Teachable Machine + Keras CNN" },
  { label: "Vector Similarity",     value: "ChromaDB + CLIP Embeddings" },
  { label: "Narrative Generation",  value: "Claude AI (Anthropic)" },
  { label: "Image Enhancement",     value: "Real-ESRGAN" },
  { label: "Backend API",           value: "Python FastAPI" },
  { label: "Frontend",              value: "React + Leaflet.js" },
];

export default function About() {
  const [ref, visible] = useReveal();

  return (
    <div className="page about-page">
      <div className="page-header">
        <h1 className="page-title">About This Project</h1>
        <p className="page-sub">AI Heritage Revive — Walled City of Lahore</p>
      </div>

      <div ref={ref} className={`about-container reveal ${visible ? "in-view" : ""}`}>
        <div className="card about-card">
          <h2 className="about-heading">What is this project?</h2>
          <p className="about-text">AI Heritage Revive is an AI-powered digital heritage guide for the Walled City of Lahore, beginning with Lahore Fort as the MVP. A user uploads a photograph of any monument, and the system identifies the location, retrieves its historical context, and displays it on an interactive map — making centuries of Mughal history accessible through a smartphone camera.</p>
        </div>

        <div className="card about-card">
          <h2 className="about-heading">Technology Stack</h2>
          <div className="about-grid">
            {techStack.map(t => (
              <div key={t.label} className="about-tech-item">
                <div className="about-tech-label">{t.label}</div>
                <div className="about-tech-value">{t.value}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="card about-card">
          <h2 className="about-heading">Data Sources</h2>
          <p className="about-text">The dataset combines field photographs collected personally at Lahore Fort, images sourced from heritage documentation websites, and historical information from <em>Lahore: A Framework for Urban Conservation</em> published by the Aga Khan Historic Cities Programme (2019).</p>
        </div>

        <div className="card about-card">
          <h2 className="about-heading">Developed By</h2>
          <p className="about-text">This project was developed as a BSCS capstone project at the University of Home Economics, Lahore. The project combines AI, computer vision, and web technologies to create a smart digital heritage guide for one of the most historically significant sites in Pakistan.</p>
        </div>
      </div>
    </div>
  );
}
