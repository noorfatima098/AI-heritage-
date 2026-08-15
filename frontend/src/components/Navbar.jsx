import { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { Menu, X } from "./Icon";
import "./Navbar.css";
  
const links = [
  { to: "/explore",  label: "Explore Monuments" },
  { to: "/map",       label: "Explore Map"       },
  { to: "/identify",  label: "Identify Landmark" },
  { to: "/ar",        label: "Augmented Reality" },
  { to: "/about",     label: "About"             },
];

export default function Navbar() {
  const { pathname } = useLocation();
  const [open, setOpen] = useState(false);

  // Close the mobile menu whenever the route changes
  useEffect(() => { setOpen(false); }, [pathname]);

  return (
    <>
      <nav className="navbar">
        <Link to="/" className="navbar-brand">
          <span className="navbar-brand-main">AI Heritage Revive</span>
          <span className="navbar-brand-sub">Walled City of Lahore</span>
        </Link>

        <div className="navbar-links">
          {links.map(l => (
            <Link
              key={l.to}
              to={l.to}
              className={`navbar-link${pathname === l.to ? " active" : ""}`}
            >
              {l.label}
            </Link>
          ))}
        </div>

        <button
          className="navbar-toggle"
          aria-label={open ? "Close menu" : "Open menu"}
          aria-expanded={open}
          onClick={() => setOpen(o => !o)}
        >
          {open ? <X /> : <Menu />}
        </button>
      </nav>

      <div className={`navbar-mobile${open ? " open" : ""}`}>
        {links.map(l => (
          <Link
            key={l.to}
            to={l.to}
            className={`navbar-link${pathname === l.to ? " active" : ""}`}
          >
            {l.label}
          </Link>
        ))}
      </div>
    </>
  );
}
