import { Link, useLocation } from "react-router-dom";

export default function Navbar() {
  const { pathname } = useLocation();

  const links = [
    { to: "/",         label: "Home"     },
    { to: "/identify", label: "Identify" },
    { to: "/explore",  label: "Explore"  },
    { to: "/about",    label: "About"    },
  ];

  return (
    <nav style={s.nav}>
      <Link to="/" style={s.brand}>
        <span style={s.brandMain}>AI Heritage Revive</span>
        <span style={s.brandSub}>Walled City of Lahore</span>
      </Link>
      <div style={s.links}>
        {links.map(l => (
          <Link
            key={l.to}
            to={l.to}
            style={{ ...s.link, ...(pathname === l.to ? s.active : {}) }}
          >
            {l.label}
          </Link>
        ))}
      </div>
    </nav>
  );
}

const s = {
  nav:       { display:"flex", justifyContent:"space-between", alignItems:"center", background:"#3D2314", padding:"14px 48px", position:"sticky", top:0, zIndex:100 },
  brand:     { textDecoration:"none", display:"flex", flexDirection:"column" },
  brandMain: { fontFamily:"'Playfair Display',serif", color:"#FAFAF8", fontSize:18, fontWeight:700, letterSpacing:.5 },
  brandSub:  { color:"#C4A882", fontSize:11, letterSpacing:1.5, textTransform:"uppercase", marginTop:2 },
  links:     { display:"flex", gap:32 },
  link:      { textDecoration:"none", color:"#C4A882", fontSize:14, fontFamily:"'Inter',sans-serif", letterSpacing:.5, fontWeight:400, paddingBottom:2, borderBottom:"2px solid transparent", transition:"all .2s" },
  active:    { color:"#FAFAF8", borderBottom:"2px solid #C4A882" },
};