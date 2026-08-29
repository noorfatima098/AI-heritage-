"""
populate_gallery_images.py

Ye script aapke AI-heritage- project ke ROOT folder mein rakh kar chalayein
(jahan `assets/`, `backend/`, `frontend/` folders sath mein hon).

Kya karta hai:
1. `assets/<monument-folder>/` se har monument ki max N images uthata hai
   (evenly spaced, taake variety achi ho — sirf first N nahi).
2. Un images ko `frontend/public/images/landmarks/` mein copy karta hai
   (agar already wahan hain to skip kar deta hai).
3. `backend/dataset/lahore_fort_dataset.json` mein har landmark ke
   `reference_images` array ko update karta hai taake usme ye saari
   images list ho jayein (pehli image = card/hero image, baqi = gallery).

Run karne ka tareeqa:
    python populate_gallery_images.py

Dry-run (kuch bhi copy/save nahi karega, sirf preview dikhayega):
    python populate_gallery_images.py --dry-run
"""

import json
import re
import shutil
import argparse
from pathlib import Path

MAX_IMAGES_PER_LANDMARK = 8

# Agar landmark id aur assets/ folder ka naam match nahi karta,
# to yahan mapping add kar dein: "landmark_id": "assets-folder-name"
ID_TO_ASSET_FOLDER_OVERRIDES = {
    # example: "diwan-i-amm": "diwan-i-aam",
}


def natural_key(path: Path):
    """Sort filenames naturally so _(2) comes before _(10)."""
    parts = re.split(r"(\d+)", path.name)
    return [int(p) if p.isdigit() else p.lower() for p in parts]


def pick_evenly_spaced(files, n):
    if len(files) <= n:
        return files
    step = len(files) / n
    indices = [int(i * step) for i in range(n)]
    return [files[i] for i in indices]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max-images", type=int, default=MAX_IMAGES_PER_LANDMARK)
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    assets_dir = root / "assets"
    dataset_path = root / "backend" / "dataset" / "lahore_fort_dataset.json"
    target_images_dir = root / "frontend" / "public" / "images" / "landmarks"

    if not assets_dir.exists():
        raise SystemExit(f"assets/ folder nahi mili: {assets_dir}")
    if not dataset_path.exists():
        raise SystemExit(f"dataset json nahi mila: {dataset_path}")

    data = json.loads(dataset_path.read_text(encoding="utf-8"))
    landmarks = data["landmarks"]

    target_images_dir.mkdir(parents=True, exist_ok=True)

    updated = 0
    skipped_no_folder = []

    for landmark in landmarks:
        lid = landmark["id"]
        folder_name = ID_TO_ASSET_FOLDER_OVERRIDES.get(lid, lid)
        folder = assets_dir / folder_name

        if not folder.exists() or not folder.is_dir():
            skipped_no_folder.append(lid)
            continue

        image_files = sorted(
            [p for p in folder.iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")],
            key=natural_key,
        )
        if not image_files:
            skipped_no_folder.append(lid)
            continue

        chosen = pick_evenly_spaced(image_files, args.max_images)
        filenames = []

        for src in chosen:
            dest_name = src.name
            dest_path = target_images_dir / dest_name
            filenames.append(dest_name)
            if not args.dry_run and not dest_path.exists():
                shutil.copy2(src, dest_path)

        print(f"{lid}: {len(filenames)} images -> {filenames}")
        landmark["reference_images"] = filenames
        updated += 1

    if skipped_no_folder:
        print("\nInn landmarks ke liye assets/ mein koi matching folder ya image nahi mili:")
        for lid in skipped_no_folder:
            print(f"  - {lid}")
        print("Agar inka folder alag naam se hai to script ke top mein ID_TO_ASSET_FOLDER_OVERRIDES mein add karein.")

    if args.dry_run:
        print(f"\n[DRY RUN] {updated} landmarks update hote (koi file save nahi hui).")
        return

    dataset_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nDone. {updated} landmarks ka reference_images update ho gaya.")
    print(f"Images copy ho gayin: {target_images_dir}")
    print(f"Dataset save ho gaya: {dataset_path}")


if __name__ == "__main__":
    main()
