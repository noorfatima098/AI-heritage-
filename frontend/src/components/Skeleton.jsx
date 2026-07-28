export function SkeletonCard() {
  return (
    <div className="card" style={{ overflow: "hidden" }}>
      <div className="skeleton" style={{ aspectRatio: "4 / 3" }} />
      <div style={{ padding: 20, display: "flex", flexDirection: "column", gap: 10 }}>
        <div className="skeleton" style={{ height: 18, width: "70%", borderRadius: 4 }} />
        <div className="skeleton" style={{ height: 12, width: "100%", borderRadius: 4 }} />
        <div className="skeleton" style={{ height: 12, width: "85%", borderRadius: 4 }} />
      </div>
    </div>
  );
}

export function SkeletonGrid({ count = 6 }) {
  return (
    <div className="explore-grid">
      {Array.from({ length: count }).map((_, i) => <SkeletonCard key={i} />)}
    </div>
  );
}

export function SkeletonLine({ width = "100%", height = 14 }) {
  return <div className="skeleton" style={{ width, height, borderRadius: 4 }} />;
}
