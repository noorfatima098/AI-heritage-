# -*- coding: utf-8 -*-
"""
generate_paper_figures.py

Regenerates the paper figures that are derived from real project data /
real code logic, instead of one-off images:

  Fig. 4 — Distribution of nearest-neighbor distances across all landmarks,
           computed from dataset/lahore_fort_dataset.json's real,
           field-captured GPS coordinates.
  Fig. 5 — The GPS re-ranking proximity-weight function actually used in
           main.py's rerank_with_location(), plotted as a function of
           distance.
  Fig. 6 — CNN training coverage vs. GPS-only fallback: how many field
           reference images each landmark actually has in the dataset,
           which is exactly what decides whether a landmark is classified
           by the CNN or routed through the gps_only path in main.py's
           /identify endpoint.
  Fig. 7 — Distribution of the 34 landmarks across historical periods
           (Mughal / Sikh / Pre-Mughal / Colonial), computed straight from
           dataset/lahore_fort_dataset.json's "period" field.
  Fig. 8 — Geographic scatter of every landmark's real GPS coordinates,
           colour-coded by CNN-trained vs. GPS-only, so the fort's actual
           layout and the two identification paths are visible together.
  Fig. 9 — The exact confidence thresholds main.py's /identify endpoint
           uses to decide "not recognised" vs. "possibly X" vs. a
           confident match (0.75 / 0.85 / 0.88), drawn as zones on a
           0-100% confidence axis.
  Fig. 10 — Number of landmarks per quadrangle/sector of the fort, from
           dataset/lahore_fort_dataset.json's "quadrangle" field.
  Fig. 11 — Frequency of the most common descriptive tags across all
           landmarks, from dataset/lahore_fort_dataset.json's "tags" field.

Run this any time dataset/lahore_fort_dataset.json changes (new landmarks,
corrected coordinates, new reference images) so the paper's figures stay in
sync with the real data, instead of going stale.

Usage (from the backend/ folder):
    python generate_paper_figures.py

Output:
    figures/distance_histogram.png
    figures/weight_function.png
    figures/training_coverage.png
    figures/period_distribution.png
    figures/geographic_scatter.png
    figures/confidence_zones.png
    figures/quadrangle_counts.png
    figures/tag_frequency.png

Requires matplotlib (not otherwise a backend dependency — install with
`pip install matplotlib --break-system-packages` if it's not already
in your environment).
"""

import os
import json
import math
import collections

import matplotlib
matplotlib.use("Agg")  # headless — no display needed to just save PNGs
import matplotlib.pyplot as plt
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "dataset", "lahore_fort_dataset.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "figures")

# These must match rerank_with_location()'s constants in main.py exactly —
# if you tune the re-ranking formula there, update these too so Fig. 5
# keeps showing the function the code actually uses.
RERANK_FLOOR = 0.6
RERANK_BOOST = 0.4
RERANK_DECAY_M = 40

# Same threshold used in main.py's GPS-only direct-identification check —
# shown as the shaded band in Fig. 4 for context, not a hard cutoff.
GPS_DRIFT_LOW_M = 15
GPS_DRIFT_HIGH_M = 30

# These must match main.py's /identify confidence gates exactly — if you
# tune those thresholds there, update these too so Fig. 9 keeps showing
# the boundaries the code actually enforces.
CONF_REJECT_MAX = 0.75    # below this -> "Landmark not recognised"
CONF_GPS_RERANK = 0.85    # below this (with GPS available) -> rerank_with_location()
CONF_CONFIDENT_MIN = 0.88  # below this (and >= 0.75) -> "Possibly <name>"


def haversine_m(lat1, lng1, lat2, lng2):
    """Distance in meters between two lat/lng points. Same formula as
    main.py's haversine_m() — kept in sync deliberately."""
    R = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def load_landmarks():
    with open(DATASET_PATH, encoding="utf-8") as f:
        data = json.load(f)
    landmarks = data["landmarks"]
    missing_coords = [l["id"] for l in landmarks if not l.get("coordinates")]
    if missing_coords:
        print(f"WARNING: {len(missing_coords)} landmark(s) have no coordinates and will be skipped: {missing_coords}")
    return [l for l in landmarks if l.get("coordinates")]


def compute_nearest_neighbor_distances(landmarks):
    """For each landmark, the distance (m) to its single closest neighbor."""
    dists = []
    for i, l1 in enumerate(landmarks):
        c1 = l1["coordinates"]
        nearest = min(
            haversine_m(c1["lat"], c1["lng"], landmarks[j]["coordinates"]["lat"], landmarks[j]["coordinates"]["lng"])
            for j in range(len(landmarks)) if j != i
        )
        dists.append(nearest)
    return dists


def plot_distance_histogram(nn_dists, out_path):
    plt.rcParams["font.family"] = "DejaVu Sans"
    fig, ax = plt.subplots(figsize=(6.5, 4))

    max_d = max(nn_dists)
    bins = list(range(0, int(max_d) + 20, 10))
    ax.hist(nn_dists, bins=bins, color="#3B4CCA", edgecolor="white", alpha=0.9)
    ax.axvspan(GPS_DRIFT_LOW_M, GPS_DRIFT_HIGH_M, color="#FF6B6B", alpha=0.15,
               label=f"Typical smartphone GPS\ndrift near stone walls ({GPS_DRIFT_LOW_M}\u2013{GPS_DRIFT_HIGH_M}m)")
    ax.set_xlabel("Nearest-neighbor distance (meters)", fontsize=11)
    ax.set_ylabel("Number of landmarks", fontsize=11)
    ax.set_title(f"Fig. 4. Distribution of Nearest-Neighbor Distances\nAcross All {len(nn_dists)} Lahore Fort Landmarks",
                 fontsize=12, fontweight="bold")
    ax.legend(fontsize=9, loc="upper right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close(fig)


def plot_weight_function(out_path):
    plt.rcParams["font.family"] = "DejaVu Sans"
    d = np.linspace(0, 150, 300)
    weight = RERANK_FLOOR + RERANK_BOOST * np.exp(-d / RERANK_DECAY_M)

    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(d, weight, color="#1E2761", linewidth=2.5)
    ax.axhline(RERANK_FLOOR, color="#999999", linestyle="--", linewidth=1,
               label=f"Floor ({RERANK_FLOOR}) \u2014 GPS influence never fully vanishes")
    ax.axvline(RERANK_DECAY_M, color="#FF6B6B", linestyle=":", linewidth=1.5,
               label=f"Decay constant ({RERANK_DECAY_M}m)")
    ax.fill_between(d, RERANK_FLOOR, weight, alpha=0.15, color="#3B4CCA")
    ax.set_xlabel("Distance from user to candidate landmark (meters)", fontsize=11)
    ax.set_ylabel(f"Proximity weight  w(d) = {RERANK_FLOOR} + {RERANK_BOOST}\u00b7e$^{{-d/{RERANK_DECAY_M}}}$", fontsize=11)
    ax.set_title("Fig. 5. GPS Re-ranking Proximity Weight vs. Distance", fontsize=12, fontweight="bold")
    ax.set_ylim(RERANK_FLOOR - 0.05, 1.02)
    ax.legend(fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close(fig)


def plot_training_coverage(landmarks, out_path):
    """
    Fig. 6 — For every landmark, how many field-captured reference images
    it has. This is the real quantity that decides, in main.py's
    /identify endpoint, whether a landmark can ever be returned by the
    CNN (classify()) or is only ever reachable through the GPS-only
    fallback (gps_only == True landmarks, which have zero training
    images by construction).
    """
    plt.rcParams["font.family"] = "DejaVu Sans"

    counts = [(l["name"], len(l.get("reference_images", [])), bool(l.get("gps_only"))) for l in landmarks]
    counts.sort(key=lambda x: x[1])
    names = [c[0] for c in counts]
    n_images = [c[1] for c in counts]
    colors = ["#FF6B6B" if c[2] else "#3B4CCA" for c in counts]

    fig, ax = plt.subplots(figsize=(7, 9))
    ax.barh(names, n_images, color=colors, edgecolor="white")
    ax.set_xlabel("Field reference images available", fontsize=11)
    ax.set_title(f"Fig. 6. CNN Training Coverage vs. GPS-Only Fallback\nAcross All {len(landmarks)} Lahore Fort Landmarks",
                 fontsize=12, fontweight="bold")
    ax.tick_params(axis="y", labelsize=7)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    from matplotlib.patches import Patch
    legend_handles = [
        Patch(color="#3B4CCA", label="Has training images (CNN-classifiable)"),
        Patch(color="#FF6B6B", label="gps_only (no training images — GPS fallback)"),
    ]
    ax.legend(handles=legend_handles, fontsize=9, loc="lower right")
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close(fig)


def plot_period_distribution(landmarks, out_path):
    """
    Fig. 7 — How the 34 landmarks are distributed across historical
    periods, read directly from each landmark's "period" field in
    dataset/lahore_fort_dataset.json.
    """
    plt.rcParams["font.family"] = "DejaVu Sans"

    period_counts = {}
    for l in landmarks:
        period_counts[l["period"]] = period_counts.get(l["period"], 0) + 1
    # Sort descending by count for a cleaner bar chart.
    periods = sorted(period_counts, key=lambda p: period_counts[p], reverse=True)
    values = [period_counts[p] for p in periods]

    fig, ax = plt.subplots(figsize=(6.5, 4))
    bars = ax.bar(periods, values, color="#1E2761", edgecolor="white")
    ax.bar_label(bars, padding=3, fontsize=10)
    ax.set_xlabel("Historical period", fontsize=11)
    ax.set_ylabel("Number of landmarks", fontsize=11)
    ax.set_title(f"Fig. 7. Distribution of All {len(landmarks)} Lahore Fort\nLandmarks by Historical Period",
                 fontsize=12, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close(fig)


def plot_geographic_scatter(landmarks, out_path):
    """
    Fig. 8 — Real GPS scatter of every landmark inside the fort, colour-
    coded by whether it's reachable via the CNN (has training images) or
    only via the gps_only fallback path in main.py's /identify endpoint.
    """
    plt.rcParams["font.family"] = "DejaVu Sans"

    fig, ax = plt.subplots(figsize=(8.5, 8.5))
    for idx, l in enumerate(landmarks):
        c = l["coordinates"]
        is_gps_only = bool(l.get("gps_only"))
        color = "#FF6B6B" if is_gps_only else "#3B4CCA"
        ax.scatter(c["lng"], c["lat"], color=color, s=55, edgecolor="white", zorder=3)
        # Alternate the label above/below the point so nearby landmarks
        # (common inside a small fort) don't stack their text on top of
        # each other as often.
        dy = 5 if idx % 2 == 0 else -9
        ax.annotate(l["name"], (c["lng"], c["lat"]), fontsize=5.5, xytext=(3, dy),
                    textcoords="offset points")

    ax.set_xlabel("Longitude", fontsize=11)
    ax.set_ylabel("Latitude", fontsize=11)
    ax.set_title(f"Fig. 8. Geographic Layout of All {len(landmarks)}\nLahore Fort Landmarks",
                 fontsize=12, fontweight="bold")
    ax.ticklabel_format(useOffset=False, style="plain")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    from matplotlib.lines import Line2D
    legend_handles = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#3B4CCA", markersize=9,
               label="Has training images (CNN-classifiable)"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#FF6B6B", markersize=9,
               label="gps_only (GPS fallback)"),
    ]
    ax.legend(handles=legend_handles, fontsize=8, loc="best")
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close(fig)


def plot_confidence_zones(out_path):
    """
    Fig. 9 — The exact confidence gates main.py's /identify endpoint
    applies to the CNN's top prediction: below CONF_REJECT_MAX it's
    rejected outright, between CONF_REJECT_MAX and CONF_CONFIDENT_MIN it's
    returned as an uncertain "Possibly <name>" match, and above
    CONF_CONFIDENT_MIN it's returned as a confident match. CONF_GPS_RERANK
    is a separate gate — below it (with GPS available) the CNN's own
    top-3 shortlist gets re-ranked by proximity before this decision runs.
    """
    plt.rcParams["font.family"] = "DejaVu Sans"

    fig = plt.figure(figsize=(9, 4))
    # Axis occupies the middle band only; everything else (title, GPS
    # callout, zone labels) is placed in figure-fraction coordinates so
    # narrow zones can never make adjacent labels collide.
    ax = fig.add_axes([0.06, 0.42, 0.9, 0.22])

    ax.axvspan(0, CONF_REJECT_MAX * 100, color="#FF6B6B", alpha=0.25)
    ax.axvspan(CONF_REJECT_MAX * 100, CONF_CONFIDENT_MIN * 100, color="#FFD166", alpha=0.35)
    ax.axvspan(CONF_CONFIDENT_MIN * 100, 100, color="#3B4CCA", alpha=0.25)
    ax.axvline(CONF_GPS_RERANK * 100, color="#1E2761", linestyle=":", linewidth=1.5)

    ax.set_xlim(0, 100)
    ax.set_ylim(0, 1)
    ax.set_yticks([])
    ax.set_xlabel("CNN confidence (%)", fontsize=11)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)

    fig.suptitle("Fig. 9. Confidence Thresholds Used by /identify", fontsize=12, fontweight="bold", y=0.97)

    # GPS re-rank callout, above the band, pointing at the 85% line.
    gps_x = 0.06 + (CONF_GPS_RERANK * 100 / 100) * 0.9
    fig.text(gps_x, 0.72, f"{int(CONF_GPS_RERANK*100)}% \u2014 GPS re-rank\ntriggers below this",
              ha="center", va="bottom", fontsize=8.5)

    # Zone labels below the band, spaced evenly across the figure width so
    # a narrow middle zone never crowds its neighbours.
    fig.text(0.22, 0.30, f"Rejected\n(< {int(CONF_REJECT_MAX*100)}%)",
              ha="center", va="top", fontsize=9.5, fontweight="bold")
    fig.text(0.58, 0.30, f"\"Possibly <name>\"\n({int(CONF_REJECT_MAX*100)}\u2013{int(CONF_CONFIDENT_MIN*100)}%)",
              ha="center", va="top", fontsize=9.5, fontweight="bold")
    fig.text(0.86, 0.30, f"Confident match\n(\u2265 {int(CONF_CONFIDENT_MIN*100)}%)",
              ha="center", va="top", fontsize=9.5, fontweight="bold")

    plt.savefig(out_path, dpi=200)
    plt.close(fig)


def plot_quadrangle_counts(landmarks, out_path):
    """
    Fig. 10 — Number of landmarks per quadrangle/sector, from each
    landmark's "quadrangle" field in dataset/lahore_fort_dataset.json.
    """
    plt.rcParams["font.family"] = "DejaVu Sans"

    counts = collections.Counter(l.get("quadrangle", "Unspecified") for l in landmarks)
    items = sorted(counts.items(), key=lambda x: x[1])
    names = [i[0] for i in items]
    values = [i[1] for i in items]

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.barh(names, values, color="#1E2761", edgecolor="white")
    ax.set_xlabel("Number of landmarks", fontsize=11)
    ax.set_title(f"Fig. 10. Landmarks per Quadrangle / Sector\n(All {len(landmarks)} Lahore Fort Landmarks)",
                 fontsize=12, fontweight="bold")
    ax.tick_params(axis="y", labelsize=7)
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close(fig)


def plot_tag_frequency(landmarks, out_path, top_n=15):
    """
    Fig. 11 — Frequency of the most common descriptive tags across all
    landmarks, from each landmark's "tags" field in
    dataset/lahore_fort_dataset.json.
    """
    plt.rcParams["font.family"] = "DejaVu Sans"

    tag_counts = collections.Counter()
    for l in landmarks:
        tag_counts.update(l.get("tags", []))
    top_tags = tag_counts.most_common(top_n)
    top_tags.reverse()  # smallest at bottom, biggest at top when using barh
    names = [t[0] for t in top_tags]
    values = [t[1] for t in top_tags]

    fig, ax = plt.subplots(figsize=(6.5, 6))
    ax.barh(names, values, color="#3B4CCA", edgecolor="white")
    ax.set_xlabel("Number of landmarks tagged", fontsize=11)
    ax.set_title(f"Fig. 11. Top {top_n} Most Common Landmark Tags", fontsize=12, fontweight="bold")
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    landmarks = load_landmarks()
    nn_dists = compute_nearest_neighbor_distances(landmarks)
    nn_dists.sort()

    print(f"Landmarks with coordinates: {len(landmarks)}")
    print(f"Nearest-neighbor distance \u2014 min: {min(nn_dists):.1f}m, "
          f"median: {nn_dists[len(nn_dists)//2]:.1f}m, max: {max(nn_dists):.1f}m")
    print(f"Under {GPS_DRIFT_HIGH_M}m from nearest neighbor: "
          f"{sum(1 for d in nn_dists if d < GPS_DRIFT_HIGH_M)} of {len(nn_dists)}")

    hist_path = os.path.join(OUTPUT_DIR, "distance_histogram.png")
    weight_path = os.path.join(OUTPUT_DIR, "weight_function.png")
    coverage_path = os.path.join(OUTPUT_DIR, "training_coverage.png")
    period_path = os.path.join(OUTPUT_DIR, "period_distribution.png")
    scatter_path = os.path.join(OUTPUT_DIR, "geographic_scatter.png")
    confidence_path = os.path.join(OUTPUT_DIR, "confidence_zones.png")
    quadrangle_path = os.path.join(OUTPUT_DIR, "quadrangle_counts.png")
    tag_path = os.path.join(OUTPUT_DIR, "tag_frequency.png")

    plot_distance_histogram(nn_dists, hist_path)
    plot_weight_function(weight_path)
    plot_training_coverage(landmarks, coverage_path)
    plot_period_distribution(landmarks, period_path)
    plot_geographic_scatter(landmarks, scatter_path)
    plot_confidence_zones(confidence_path)
    plot_quadrangle_counts(landmarks, quadrangle_path)
    plot_tag_frequency(landmarks, tag_path)

    print(f"\nWrote {hist_path}")
    print(f"Wrote {weight_path}")
    print(f"Wrote {coverage_path}")
    print(f"Wrote {period_path}")
    print(f"Wrote {scatter_path}")
    print(f"Wrote {confidence_path}")
    print(f"Wrote {quadrangle_path}")
    print(f"Wrote {tag_path}")


if __name__ == "__main__":
    main()