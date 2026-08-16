import useReveal from "../hooks/useReveal";
import "./About.css";

const techStack = [
  { label: "Image Classification", value: "Google Teachable Machine + Keras CNN" },
  { label: "Vector Similarity",     value: "ChromaDB + CLIP Embeddings" },
  { label: "Narrative Generation",  value: "Groq AI (Llama 3.3-70B)" },
  { label: "Image Enhancement",     value: "Real-ESRGAN" },
  { label: "Backend API",           value: "Python FastAPI" },
  { label: "Frontend",              value: "React + Leaflet.js" },
  { label: "Conversational Assistant",              value: "Groq (Llama 3.3-70B) + ChromaDB RAG" },
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
          <p className="about-text">AI Heritage Revive is an AI-powered digital heritage guide for the Walled City of Lahore, beginning with Lahore Fort as the MVP. A user uploads a photograph of any monument, and the system identifies the location, retrieves its historical context, and displays it on an interactive map — making centuries of Mughal history accessible through a smartphone camera.A built-in AI chatbot lets visitors ask questions directly and get context-aware answers grounded in curated heritage documentation.</p>
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
          <p className="about-text">The dataset combines field photographs collected personally at Lahore Fort, images sourced from heritage documentation websites, and historical information from Lahore: A Framework for Urban Conservation published by the Aga Khan Historic Cities Programme (2019), along with The Walled City of Lahore (Second Edition, 2009, Sustainable Development of Walled City of Lahore Project — SDWCLP).</p>
        </div>

        <div className="card about-card">
          <h2 className="about-heading">Developed By</h2>
          <p className="about-text">AI Heritage Revive is a BSCS capstone project developed by students at the University of Home Economics, Lahore. The project brings together artificial intelligence, computer vision, and modern web technologies to reimagine how people discover and engage with historical landmarks. From training a custom image classification model to designing an intuitive, map-based interface, every layer of this system was built with the goal of making Lahore's rich Mughal-era heritage more accessible to everyday visitors. This is an ongoing effort, with plans to expand coverage beyond Lahore Fort to the entire Walled City in future iterations.</p>
        </div>
      </div>
    </div>
  );
}
