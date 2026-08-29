# -*- coding: utf-8 -*-
"""
generate_paper_figures.py

Regenerates the two paper figures that are derived from real project data /
real code logic, instead of one-off images:

  Fig. 4 — Distribution of nearest-neighbor distances across all landmarks,
           computed from dataset/lahore_fort_dataset.json's real,
           field-captured GPS coordinates.
  Fig. 5 — The GPS re-ranking proximity-weight function actually used in
           main.py's rerank_with_location(), plotted as a function of
           distance.

Run this any time dataset/lahore_fort_dataset.json changes (new landmarks,
corrected coordinates) so the paper's figures stay in sync with the real
data, instead of going stale.

Usage (from the backend/ folder):
    python generate_paper_figures.py

Output:
    figures/distance_histogram.png
    figures/weight_function.png

Requires matplotlib (not otherwise a backend dependency — install with
`pip install matplotlib --break-system-packages` if it's not already
in your environment).
"""

import os
import json
import math

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

    plot_distance_histogram(nn_dists, hist_path)
    plot_weight_function(weight_path)

    print(f"\nWrote {hist_path}")
    print(f"Wrote {weight_path}")


if __name__ == "__main__":
    main()
