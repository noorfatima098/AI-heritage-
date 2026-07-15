import { useNavigate } from "react-router-dom";

export default function Home() {
  const nav = useNavigate();

  return (
    <div style={s.page}>

      {/* Hero */}
      <div style={s.hero}>
        <div style={s.arch} />
        <div style={s.heroContent}>
          <p style={s.eyebrow}>Lahore Fort · Mughal Heritage · AI-Powered</p>
          <h1 style={s.title}>Discover the Walled<br />City of Lahore</h1>
          <p style={s.subtitle}>
            Upload a photograph of any monument inside Lahore Fort and let AI
            reveal its history, architecture, and exact location on the map.
          </p>
          <div style={s.btnRow}>
            <button style={s.btnPrimary} onClick={() => nav("/identify")}>
              🔍  Identify a Landmark
            </button>
            <button style={s.btnSecondary} onClick={() => nav("/explore")}>
              🗺  Explore the Map
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

const s = {
  page:        { fontFamily:"'Inter',sans-serif" },
  hero:        { minHeight:"88vh", background:"linear-gradient(160deg, #3D2314 0%, #5C3520 55%, #7B4F2E 100%)", display:"flex", alignItems:"center", justifyContent:"center", position:"relative", overflow:"hidden", padding:"60px 24px" },
  arch:        { position:"absolute", bottom:-80, right:-80, width:420, height:420, borderRadius:"50% 50% 0 0", border:"2px solid rgba(196,168,130,0.15)", background:"transparent" },
  heroContent: { maxWidth:680, textAlign:"center", position:"relative", zIndex:2 },
  eyebrow:     { color:"#C4A882", fontSize:12, letterSpacing:3, textTransform:"uppercase", marginBottom:20, fontWeight:400 },
  title:       { fontFamily:"'Playfair Display',serif", color:"#FAFAF8", fontSize:"clamp(36px,6vw,64px)", lineHeight:1.15, fontWeight:700, marginBottom:24 },
  subtitle:    { color:"rgba(250,250,248,0.75)", fontSize:17, lineHeight:1.8, marginBottom:44, fontWeight:300 },
  btnRow:      { display:"flex", gap:16, justifyContent:"center", flexWrap:"wrap" },
  btnPrimary:  { background:"#C4A882", color:"#3D2314", border:"none", padding:"15px 36px", borderRadius:4, fontSize:15, fontWeight:600, cursor:"pointer", fontFamily:"'Inter',sans-serif", letterSpacing:.5 },
  btnSecondary:{ background:"transparent", color:"#C4A882", border:"2px solid #C4A882", padding:"15px 36px", borderRadius:4, fontSize:15, fontWeight:500, cursor:"pointer", fontFamily:"'Inter',sans-serif", letterSpacing:.5 },
  features:    { display:"grid", gridTemplateColumns:"repeat(auto-fit,minmax(260px,1fr))", gap:0, background:"#EEEBE4" },
  card:        { padding:"52px 40px", borderRight:"1px solid #DDD9D0" },
  icon:        { fontSize:32, marginBottom:16 },
  cardTitle:   { fontFamily:"'Playfair Display',serif", fontSize:20, fontWeight:600, color:"#3D2314", marginBottom:12 },
  cardDesc:    { color:"#6B6560", fontSize:15, lineHeight:1.7, fontWeight:300 },
  stats:       { display:"grid", gridTemplateColumns:"repeat(4,1fr)", background:"#3D2314", padding:"48px" },
  stat:        { textAlign:"center", padding:"16px" },
  statNum:     { fontFamily:"'Playfair Display',serif", fontSize:36, color:"#C4A882", fontWeight:700 },
  statLabel:   { color:"rgba(250,250,248,0.6)", fontSize:12, letterSpacing:2, textTransform:"uppercase", marginTop:6 },
};