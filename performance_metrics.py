
import os
import numpy as np
import tensorflow as tf
import tf_keras

import matplotlib.pyplot as plt

from PIL import Image
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay
)

# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR, "backend", "model", "keras_model.h5"
)

LABELS_PATH = os.path.join(
    BASE_DIR, "backend", "model", "labels.txt"
)

ASSETS_PATH = os.path.join(
    BASE_DIR, "assets"
)

OUTPUT_PATH = os.path.join(
    BASE_DIR, "backend", "figures"
)

os.makedirs(OUTPUT_PATH, exist_ok=True)


# ============================================================
# SETTINGS
# ============================================================

IMAGE_SIZE = (224, 224)


# ============================================================
# LOAD LABELS
# ============================================================

with open(LABELS_PATH, "r", encoding="utf-8") as f:
    labels = [line.strip() for line in f.readlines() if line.strip()]

# Remove Teachable Machine numbering if present
clean_labels = []

for label in labels:
    parts = label.split(" ", 1)

    if len(parts) == 2 and parts[0].isdigit():
        clean_labels.append(parts[1])
    else:
        clean_labels.append(label)

labels = clean_labels

print("\nClasses found:")
for i, label in enumerate(labels):
    print(f"{i}: {label}")


# ============================================================
# LOAD MODEL
# ============================================================

print("\nLoading model...")

model = tf_keras.models.load_model(
    MODEL_PATH,
    compile=False
)

print("Model loaded successfully!")


# ============================================================
# LOAD IMAGES FROM ASSETS
# ============================================================

image_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".webp")

y_true = []
y_pred = []

total_images = 0

print("\nScanning dataset...\n")

for class_index, class_name in enumerate(labels):

    class_folder = os.path.join(ASSETS_PATH, class_name)

    if not os.path.isdir(class_folder):
        print(f"WARNING: Folder not found: {class_folder}")
        continue

    images = [
        file for file in os.listdir(class_folder)
        if file.lower().endswith(image_extensions)
    ]

    print(f"{class_name}: {len(images)} images")

    for image_name in images:

        image_path = os.path.join(
            class_folder,
            image_name
        )

        try:
            image = Image.open(image_path).convert("RGB")

            image = image.resize(IMAGE_SIZE)

            image_array = np.asarray(image, dtype=np.float32)

            # Normalize exactly like common Teachable Machine models
            image_array = (image_array / 127.5) - 1.0

            image_array = np.expand_dims(
                image_array,
                axis=0
            )

            prediction = model.predict(
                image_array,
                verbose=0
            )

            predicted_class = int(
                np.argmax(prediction[0])
            )

            y_true.append(class_index)
            y_pred.append(predicted_class)

            total_images += 1

        except Exception as e:
            print(
                f"Error processing {image_name}: {e}"
            )


# ============================================================
# CHECK DATA
# ============================================================

if total_images == 0:
    print("\nERROR: No images were found.")
    print("Check your assets folder and class names.")
    exit()

print("\n========================================")
print("EVALUATION COMPLETE")
print("========================================")

print(f"Total images evaluated: {total_images}")


# ============================================================
# METRICS
# ============================================================

accuracy = accuracy_score(
    y_true,
    y_pred
)

precision = precision_score(
    y_true,
    y_pred,
    average="weighted",
    zero_division=0
)

recall = recall_score(
    y_true,
    y_pred,
    average="weighted",
    zero_division=0
)

f1 = f1_score(
    y_true,
    y_pred,
    average="weighted",
    zero_division=0
)


# ============================================================
# PRINT RESULTS
# ============================================================

print("\n========================================")
print("PERFORMANCE METRICS")
print("========================================")

print(f"Accuracy  : {accuracy * 100:.2f}%")
print(f"Precision : {precision * 100:.2f}%")
print(f"Recall    : {recall * 100:.2f}%")
print(f"F1 Score  : {f1 * 100:.2f}%")


# ============================================================
# CLASSIFICATION REPORT
# ============================================================

print("\n========================================")
print("CLASSIFICATION REPORT")
print("========================================")

report = classification_report(
    y_true,
    y_pred,
    labels=list(range(len(labels))),
    target_names=labels,
    zero_division=0
)

print(report)


# ============================================================
# SAVE CLASSIFICATION REPORT
# ============================================================

report_path = os.path.join(
    OUTPUT_PATH,
    "classification_report.txt"
)

with open(
    report_path,
    "w",
    encoding="utf-8"
) as f:

    f.write("AI HERITAGE REVIVE\n")
    f.write("Model Performance Evaluation\n")
    f.write("=" * 60 + "\n\n")

    f.write(
        f"Total Images: {total_images}\n\n"
    )

    f.write(
        f"Accuracy  : {accuracy * 100:.2f}%\n"
    )

    f.write(
        f"Precision : {precision * 100:.2f}%\n"
    )

    f.write(
        f"Recall    : {recall * 100:.2f}%\n"
    )

    f.write(
        f"F1 Score  : {f1 * 100:.2f}%\n\n"
    )

    f.write("=" * 60 + "\n")
    f.write("CLASSIFICATION REPORT\n")
    f.write("=" * 60 + "\n\n")

    f.write(report)


# ============================================================
# CONFUSION MATRIX
# ============================================================

cm = confusion_matrix(
    y_true,
    y_pred,
    labels=list(range(len(labels)))
)

fig, ax = plt.subplots(
    figsize=(14, 12)
)

disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=labels
)

disp.plot(
    ax=ax,
    xticks_rotation=90,
    cmap="Blues",
    colorbar=True
)

plt.title(
    "AI Heritage Revive - Confusion Matrix"
)

plt.tight_layout()

confusion_path = os.path.join(
    OUTPUT_PATH,
    "confusion_matrix.png"
)

plt.savefig(
    confusion_path,
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# FINAL
# ============================================================

print("\n========================================")
print("FILES SAVED")
print("========================================")

print(
    f"Classification report:\n{report_path}"
)

print(
    f"Confusion matrix:\n{confusion_path}"
)

print("\nDone!")
