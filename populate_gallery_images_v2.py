"""
populate_gallery_images_v2.py  (FIXED VERSION)

Pehli script ne galti se har landmark ki CARD image (reference_images[0])
bhi replace kar di thi. Ye version us galti ko fix karta hai:

- Har landmark ki ORIGINAL card image (jo pehle se dataset mein thi)
  wapas [0] position pe rakhi jati hai — card pe wahi purani image dikhegi.
- Uske baad 7 (ya jitni chahiye) additional images add hoti hain gallery ke liye,
  evenly spaced, original wali ko chhor kar (duplicate na ho).

Run karne ka tareeqa (isi project root mein, jahan assets/backend/frontend hain):
    python populate_gallery_images_v2.py --dry-run   (pehle preview)
    python populate_gallery_images_v2.py             (real run)
"""

import json
import re
import shutil
import argparse
from pathlib import Path

MAX_IMAGES_PER_LANDMARK = 8

# Yeh original card images hain (jo aapke dataset mein pehle se thin,
# is script se pehle). Inhe hamesha [0] position pe rakha jayega.
ORIGINAL_CARD_IMAGE = {
    "sheesh-mahal": "sheesh-mahal_(31)_field.JPG",
    "picture-wall": "picture-wall_(23)_field.JPG",
    "jahangir-quadrangle": "jahangir-quadrangle_(81)_field.JPG",
    "arz-gah": "arz-gah_(32)_field.JPG",
    "shah-jahan-quadrangle": "shah-jahan-quadrangle_(53)_field.JPG",
    "lal-burj": "lal-burj_(89)_field.JPG",
    "haveli-mai-jindan": "haveli-mai-jindan_(40)_field.JPG",
    "moti-masjid": "moti-masjid_(76)_field.JPG",
    "maktab-khana": "maktab-khana_(90)_field.JPG",
    # NOTE: original dataset had this filename WITHOUT ".JPG" (a pre-existing
    # bug — it never actually loaded on the card either). Corrected here:
    "doulat-khana": "doulat-khana_(71)_field.JPG",
    "diwan-i-amm": "diwan-i-amm_(63)_field.JPG",
    "shah-burj-gate": "shah-burj-gate_(1)_field.JPG",
    "barood-khana": "barood-khana_(55)_field.JPG",
    "alamgiri-gate": "alamgiri-gate_(93)_field.JPG",
    "royal-kitchen": "royal-kitchen_(36)_field.JPG",
    "akbari-gate": "akbari-gate_(24)_field.JPG",
    "hathi-paer-stairs": "hathi-paer-stairs_(65)_field.JPG",
}

# Agar landmark id aur assets/ folder ka naam match nahi karta,
# to yahan mapping add kar dein: "landmark_id": "assets-folder-name"
ID_TO_ASSET_FOLDER_OVERRIDES = {
    # example: "diwan-i-amm": "diwan-i-aam",
}


def natural_key(path: Path):
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

        card_image = ORIGINAL_CARD_IMAGE.get(lid)
        remaining_count = args.max_images - (1 if card_image else 0)

        # Gallery ke liye evenly-spaced picks, card image ko exclude karke
        pool = [p for p in image_files if p.name != card_image]
        chosen_extra = pick_evenly_spaced(pool, remaining_count)

        filenames = []
        if card_image:
            filenames.append(card_image)
        filenames.extend(p.name for p in chosen_extra)

        # Sab files copy karein (card image bhi, kyunki naye folder mein na ho to)
        for name in filenames:
            src = folder / name
            dest_path = target_images_dir / name
            if not args.dry_run and src.exists() and not dest_path.exists():
                shutil.copy2(src, dest_path)

        print(f"{lid}: {len(filenames)} images -> {filenames}")
        landmark["reference_images"] = filenames
        updated += 1

    if skipped_no_folder:
        print("\nInn landmarks ke liye assets/ mein koi matching folder ya image nahi mili:")
        for lid in skipped_no_folder:
            print(f"  - {lid}")

    if args.dry_run:
        print(f"\n[DRY RUN] {updated} landmarks update hote (koi file save nahi hui).")
        return

    dataset_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nDone. {updated} landmarks ka reference_images update ho gaya (card image restore ho gayi + gallery images add ho gayin).")
    print(f"Images copy ho gayin: {target_images_dir}")
    print(f"Dataset save ho gaya: {dataset_path}")


if __name__ == "__main__":
    main()
