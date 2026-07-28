import { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import axios from "axios";
import MonumentArt from "../components/MonumentArt";
import { SkeletonLine } from "../components/Skeleton";
import { MapPin, Compass, BookOpen, Sparkle, ArrowRight } from "../components/Icon";
import "./MonumentDetail.css";

export default function MonumentDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [landmark, setLandmark] = useState(null);
  const [loading, setLoading]   = useState(true);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    setLoading(true);
    setNotFound(false);
    axios.get("http://localhost:8000/landmarks")
      .then(res => {
        const found = (res.data.landmarks || []).find(l => l.id === id);
        if (found) setLandmark(found); else setNotFound(true);
      })
      .catch(() => setNotFound(true))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="page detail-page">
        <div className="detail-hero skeleton" />
        <div className="container" style={{ padding: "36px 24px", display: "flex", flexDirection: "column", gap: 14 }}>
          <SkeletonLine width="40%" height={30} />
          <SkeletonLine width="90%" />
          <SkeletonLine width="75%" />
        </div>
      </div>
    );
  }

  if (notFound || !landmark) {
    return (
      <div className="page detail-page">
        <div className="container" style={{ padding: "80px 24px", textAlign: "center" }}>
          <h1 className="page-title" style={{ color: "var(--brown-dark)" }}>Monument not found</h1>
          <p className="page-sub" style={{ color: "var(--grey-mid)", margin: "12px auto 28px" }}>
            We couldn't find that landmark — it may have moved or the link is out of date.
          </p>
          <button className="btn btn-solid" onClick={() => navigate("/explore")}>Back to Explore</button>
        </div>
      </div>
    );
  }

  const {
    name, name_urdu, description, short_description, historical_background,
    architecture, architecture_details, facts, interesting_facts, gallery, images,
    built_by, year_built, period, significance, coordinates, image_url, image,
  } = landmark;

  const body = description || short_description;
  const history = historical_background;
  const arch = architecture || architecture_details;
  const factList = facts || interesting_facts || [];
  const galleryImages = gallery || images || [];

  return (
    <div className="page detail-page">
      <div className="detail-hero">
        <MonumentArt id={id} name={name} src={image_url || image} rounded="0" aspect="16 / 7" />
        <div className="detail-hero-overlay">
          <div className="container">
            <Link to="/explore" className="detail-back">← Back to Explore</Link>
            <h1 className="detail-hero-title">{name}</h1>
            {name_urdu && <p className="detail-hero-urdu">{name_urdu}</p>}
          </div>
        </div>
      </div>

      <div className="container detail-container">
        <div className="detail-main">
          {body && (
            <section className="detail-card card">
              <h2 className="detail-heading"><BookOpen size={18} /> Overview</h2>
              <p className="detail-text">{body}</p>
            </section>
          )}

          {history && (
            <section className="detail-card card">
              <h2 className="detail-heading"><BookOpen size={18} /> Historical Background</h2>
              <p className="detail-text">{history}</p>
            </section>
          )}

          {arch && (
            <section className="detail-card card">
              <h2 className="detail-heading"><Compass size={18} /> Architecture</h2>
              <p className="detail-text">{arch}</p>
            </section>
          )}

          {factList.length > 0 && (
            <section className="detail-card card">
              <h2 className="detail-heading"><Sparkle size={18} /> Interesting Facts</h2>
              <ul className="detail-facts">
                {factList.map((f, i) => <li key={i}>{f}</li>)}
              </ul>
            </section>
          )}

          {galleryImages.length > 0 && (
            <section className="detail-card card">
              <h2 className="detail-heading"><Sparkle size={18} /> Gallery</h2>
              <div className="detail-gallery">
                {galleryImages.map((src, i) => (
                  <div key={i} className="detail-gallery-item">
                    <img src={src} alt={`${name} ${i + 1}`} loading="lazy" />
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>

        <aside className="detail-side">
          <div className="detail-card card detail-info">
            <h3 className="detail-info-title">At a Glance</h3>
            {built_by && <div className="detail-info-row"><span>Built by</span><strong>{built_by}</strong></div>}
            {year_built && <div className="detail-info-row"><span>Year</span><strong>{year_built}</strong></div>}
            {period && <div className="detail-info-row"><span>Period</span><strong>{period}</strong></div>}
            {significance && <div className="detail-info-row"><span>Significance</span><strong>{significance}</strong></div>}
          </div>

          {coordinates && (
            <button
              className="btn btn-solid btn-block"
              onClick={() => navigate(`/map?focus=${id}`)}
            >
              <MapPin size={16} /> View on Map <ArrowRight size={14} />
            </button>
          )}
        </aside>
      </div>
    </div>
  );
}
