import { useState } from "react";

// Deterministic tone variation so different monuments feel distinct
// while staying inside the brown/grey palette.
function toneFor(id = "") {
  let hash = 0;
  for (let i = 0; i < id.length; i++) hash = (hash * 31 + id.charCodeAt(i)) >>> 0;
  const tones = [
    ["#7B4F2E", "#3D2314"],
    ["#8C8580", "#4A4747"],
    ["#C4A882", "#7B4F2E"],
    ["#5C3520", "#3D2314"],
  ];
  return tones[hash % tones.length];
}

/**
 * Renders a real photo if `src` resolves, otherwise falls back to a
 * generated Mughal-arch illustration in the site palette — so cards
 * never show a broken image while real photography is still being wired up.
 */
export default function MonumentArt({ id, name, src, aspect = "4 / 3", rounded = "16px", topOnly = false }) {
  const [failed, setFailed] = useState(!src);
  const [from, to] = toneFor(id || name || "monument");
  const gradId = `g-${(id || name || "m").replace(/[^a-z0-9]/gi, "")}`;

  const radiusStyle = topOnly
    ? { borderTopLeftRadius: rounded, borderTopRightRadius: rounded }
    : { borderRadius: rounded };

  if (!failed) {
    return (
      <div style={{ aspectRatio: aspect, overflow: "hidden", ...radiusStyle }}>
        <img
          src={src}
          alt={name}
          onError={() => setFailed(true)}
          style={{ width: "100%", height: "100%", objectFit: "cover", display: "block" }}
        />
      </div>
    );
  }

  return (
    <div style={{ aspectRatio: aspect, ...radiusStyle, overflow: "hidden", position: "relative" }}>
      <svg viewBox="0 0 400 300" width="100%" height="100%" preserveAspectRatio="xMidYMid slice" style={{ display: "block" }}>
        <defs>
          <linearGradient id={gradId} x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor={from} />
            <stop offset="100%" stopColor={to} />
          </linearGradient>
        </defs>
        <rect width="400" height="300" fill={`url(#${gradId})`} />
        {/* faint repeating arch silhouettes, evoking the fort's arcades */}
        {[0, 1, 2, 3, 4].map((i) => (
          <path
            key={i}
            d={`M${i * 90 - 20},300 L${i * 90 - 20},210 Q${i * 90 + 25},150 ${i * 90 + 70},210 L${i * 90 + 70},300 Z`}
            fill="rgba(250,250,248,0.08)"
          />
        ))}
        <circle cx="335" cy="55" r="30" fill="rgba(250,250,248,0.06)" />
        {/* monogram initial */}
        <text
          x="200" y="175"
          textAnchor="middle"
          fontFamily="'Outfit', sans-serif"
          fontSize="64"
          fontWeight="700"
          fill="rgba(250,250,248,0.24)"
        >
          {(name || "?").trim().charAt(0).toUpperCase()}
        </text>
      </svg>
    </div>
  );
}
