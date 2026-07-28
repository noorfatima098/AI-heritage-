import { useEffect, useRef, useState } from "react";

// Adds "in-view" class the first time an element scrolls into the viewport.
// Usage: const [ref, visible] = useReveal();  <div ref={ref} className={`reveal ${visible ? "in-view" : ""}`}>
export default function useReveal(threshold = 0.15) {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true);
          observer.unobserve(el);
        }
      },
      { threshold }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, [threshold]);

  return [ref, visible];
}
