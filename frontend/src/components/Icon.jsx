// Small hand-rolled icon set — keeps the project dependency-free.
const base = { fill: "none", stroke: "currentColor", strokeWidth: 1.8, strokeLinecap: "round", strokeLinejoin: "round" };

export function Search({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" {...base}>
      <circle cx="11" cy="11" r="7" />
      <path d="M21 21l-4.35-4.35" />
    </svg>
  );
}

export function MapPin({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" {...base}>
      <path d="M12 21s-7-6.1-7-11a7 7 0 0 1 14 0c0 4.9-7 11-7 11Z" />
      <circle cx="12" cy="10" r="2.4" />
    </svg>
  );
}

export function Camera({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" {...base}>
      <path d="M4 8h3l1.6-2.4h6.8L17 8h3a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1Z" />
      <circle cx="12" cy="13.5" r="3.6" />
    </svg>
  );
}

export function Sparkle({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2c.6 3.9 2 5.7 6 6.3-4 .6-5.4 2.4-6 6.3-.6-3.9-2-5.7-6-6.3 4-.6 5.4-2.4 6-6.3ZM19 15c.3 1.9 1 2.6 2.8 2.9-1.8.3-2.5 1-2.8 2.9-.3-1.9-1-2.6-2.8-2.9 1.8-.3 2.5-1 2.8-2.9Z" />
    </svg>
  );
}

export function ArrowRight({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" {...base}>
      <path d="M5 12h14" />
      <path d="M13 6l6 6-6 6" />
    </svg>
  );
}

export function Menu({ size = 24 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" {...base}>
      <path d="M4 7h16M4 12h16M4 17h16" />
    </svg>
  );
}

export function X({ size = 24 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" {...base}>
      <path d="M6 6l12 12M18 6L6 18" />
    </svg>
  );
}

export function BookOpen({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" {...base}>
      <path d="M12 5c-1.8-1.2-4.2-1.6-6.5-1v13c2.3-.6 4.7-.2 6.5 1 1.8-1.2 4.2-1.6 6.5-1V4c-2.3-.6-4.7-.2-6.5 1Z" />
      <path d="M12 5v13" />
    </svg>
  );
}

export function Hammer({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" {...base}>
      <path d="M14.5 5.5 18.5 9.5" />
      <path d="M4 20l6.5-6.5" />
      <path d="M9.5 8.5 6 5l2-2 3.5 3.5" />
      <path d="M13 9l7.5 7.5-2 2L11 11" />
    </svg>
  );
}

export function ImageIcon({ size = 20 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" {...base}>
      <rect x="3" y="4" width="18" height="16" rx="2" />
      <circle cx="8.5" cy="9.5" r="1.6" />
      <path d="M21 16l-5.5-5.5a1.5 1.5 0 0 0-2.1 0L4 19" />
    </svg>
  );
}

export function Compass({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" {...base}>
      <circle cx="12" cy="12" r="9" />
      <path d="M15 9l-2 6-4 2 2-6 4-2Z" />
    </svg>
  );
}

export function ChevronDown({ size = 16 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" {...base}>
      <path d="M6 9l6 6 6-6" />
    </svg>
  );
}
