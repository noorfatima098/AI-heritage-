import { useState, useEffect, useMemo } from "react";
import axios from "axios";
import useReveal from "../hooks/useReveal";
import MonumentCard from "../components/MonumentCard";
import { SkeletonGrid } from "../components/Skeleton";
import { Search } from "../components/Icon";
import "./Explore.css";

export default function Explore() {
  const [landmarks, setLandmarks] = useState([]);
  const [loading, setLoading]     = useState(true);
  const [error, setError]         = useState(null);
  const [query, setQuery]         = useState("");
  const [period, setPeriod]       = useState("All");
  const [headerRef, headerVisible] = useReveal();

  useEffect(() => {
    axios.get("http://localhost:8000/landmarks")
      .then(res => setLandmarks(res.data.landmarks || []))
      .catch(() => setError("Backend se landmarks nahi mile. FastAPI chal raha hai?"))
      .finally(() => setLoading(false));
  }, []);

  const periods = useMemo(() => {
    const set = new Set(landmarks.map(l => l.period).filter(Boolean));
    return ["All", ...Array.from(set)];
  }, [landmarks]);

  const filtered = useMemo(() => {
    return landmarks.filter(l => {
      const matchesQuery = !query || [l.name, l.name_urdu, l.description, l.built_by]
        .filter(Boolean).some(f => f.toLowerCase().includes(query.toLowerCase()));
      const matchesPeriod = period === "All" || l.period === period;
      return matchesQuery && matchesPeriod;
    });
  }, [landmarks, query, period]);

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Explore the Monuments</h1>
        <p className="page-sub">Eleven landmarks of Lahore Fort, each with its own story of empire, art, and architecture.</p>
      </div>

      <div className="container" style={{ padding: "36px 24px 72px" }}>
        <div ref={headerRef} className={`explore-controls reveal ${headerVisible ? "in-view" : ""}`}>
          <div className="explore-search">
            <Search size={17} />
            <input
              className="input"
              style={{ border: "none", boxShadow: "none", padding: "0 0 0 8px" }}
              placeholder="Search monuments by name, builder, or era…"
              value={query}
              onChange={e => setQuery(e.target.value)}
            />
          </div>
          {periods.length > 1 && (
            <div className="explore-filters">
              {periods.map(p => (
                <button
                  key={p}
                  className={`chip${period === p ? " active" : ""}`}
                  onClick={() => setPeriod(p)}
                >
                  {p}
                </button>
              ))}
            </div>
          )}
        </div>

        {error && <p className="explore-error">{error}</p>}

        {loading ? (
          <SkeletonGrid count={8} />
        ) : filtered.length === 0 ? (
          <div className="explore-empty">
            <p>No monuments match your search just yet — try a different name or era.</p>
          </div>
        ) : (
          <div className="explore-grid">
            {filtered.map((l, i) => (
              <div key={l.id} className="explore-grid-item" style={{ animationDelay: `${Math.min(i, 8) * 45}ms` }}>
                <MonumentCard landmark={l} />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
