export default function About() {
  return (
    <div style={s.page}>
      <div style={s.header}>
        <h1 style={s.title}>About This Project</h1>
        <p style={s.sub}>AI Heritage Revive — Walled City of Lahore</p>
      </div>

      <div style={s.container}>
        <div style={s.card}>
          <h2 style={s.heading}>What is this project?</h2>
          <p style={s.text}>AI Heritage Revive is an AI-powered digital heritage guide for the Walled City of Lahore, beginning with Lahore Fort as the MVP. A user uploads a photograph of any monument, and the system identifies the location, retrieves its historical context, and displays it on an interactive map — making centuries of Mughal history accessible through a smartphone camera.</p>
        </div>

        <div style={s.card}>
          <h2 style={s.heading}>Technology Stack</h2>
          <div style={s.grid}>
            {[
              { label:"Image Classification", value:"Google Teachable Machine + Keras CNN" },
              { label:"Vector Similarity",     value:"ChromaDB + CLIP Embeddings"          },
              { label:"Narrative Generation",  value:"Claude AI (Anthropic)"               },
              { label:"Image Enhancement",     value:"Real-ESRGAN"                         },
              { label:"Backend API",           value:"Python FastAPI"                      },
              { label:"Frontend",              value:"React + Leaflet.js"                  },
            ].map(t => (
              <div key={t.label} style={s.techItem}>
                <div style={s.techLabel}>{t.label}</div>
                <div style={s.techValue}>{t.value}</div>
              </div>
            ))}
          </div>
        </div>

        <div style={s.card}>
          <h2 style={s.heading}>Data Sources</h2>
          <p style={s.text}>The dataset combines field photographs collected personally at Lahore Fort, images sourced from heritage documentation websites, and historical information from <em>Lahore: A Framework for Urban Conservation</em> published by the Aga Khan Historic Cities Programme (2019).</p>
        </div>

        <div style={s.card}>
          <h2 style={s.heading}>Developed By</h2>
          <p style={s.text}>This project was developed as a BSCS capstone project at the University of Home Economics, Lahore. The project combines AI, computer vision, and web technologies to create a smart digital heritage guide for one of the most historically significant sites in Pakistan.</p>
        </div>
      </div>
    </div>
  );
}

const s = {
  page:      { minHeight:"100vh", background:"#FAFAF8", fontFamily:"'Inter',sans-serif" },
  header:    { background:"#3D2314", padding:"48px", textAlign:"center" },
  title:     { fontFamily:"'Playfair Display',serif", color:"#FAFAF8", fontSize:36, fontWeight:700, marginBottom:10 },
  sub:       { color:"#C4A882", fontSize:15, fontWeight:300 },
  container: { maxWidth:780, margin:"0 auto", padding:"40px 24px", display:"flex", flexDirection:"column", gap:20 },
  card:      { background:"#fff", border:"1px solid #E8E4DC", borderRadius:8, padding:32 },
  heading:   { fontFamily:"'Playfair Display',serif", fontSize:22, color:"#3D2314", fontWeight:600, marginBottom:16 },
  text:      { color:"#4A4747", lineHeight:1.85, fontSize:15 },
  grid:      { display:"grid", gridTemplateColumns:"1fr 1fr", gap:16 },
  techItem:  { background:"#EEEBE4", borderRadius:6, padding:"14px 18px" },
  techLabel: { fontSize:11, color:"#8C8580", textTransform:"uppercase", letterSpacing:1.5, marginBottom:6 },
  techValue: { fontSize:14, color:"#3D2314", fontWeight:500 },
};