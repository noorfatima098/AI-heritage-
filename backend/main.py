import tempfile
import shutil
import os
import json

from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import tf_keras
import numpy as np
from PIL import Image

app = FastAPI()

# Load model and dataset once at startup
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Base directory (backend/ folder)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load model and dataset once at startup
model = tf_keras.models.load_model(os.path.join(BASE_DIR, 'model', 'keras_model.h5'))
labels = open(os.path.join(BASE_DIR, 'model', 'labels.txt')).read().splitlines()
dataset = json.load(open(os.path.join(BASE_DIR, 'dataset', 'lahore_fort_dataset.json'), encoding='utf-8'))

def classify(image_path):
    img  = Image.open(image_path).resize((224, 224)).convert("RGB")
    arr  = np.array(img, dtype=np.float32) / 255.0
    arr  = np.expand_dims(arr, axis=0)
    pred = model.predict(arr)[0]
    idx  = np.argmax(pred)
    return labels[idx].split(" ", 1)[-1].lower().replace(" ", "-"), float(pred[idx])

@app.post("/identify")
async def identify(file: UploadFile):
    tmp = os.path.join(tempfile.gettempdir(), file.filename)
    with open(tmp, "wb") as f:
        shutil.copyfileobj(file.file, f)

    landmark_id, confidence = classify(tmp)
    os.remove(tmp)
    print(f"DEBUG: {landmark_id} = {confidence}")

    if landmark_id == "other" or confidence < 0.75:
        return {"recognised": False, "message": "Landmark not recognised. Try a clearer photo."}

    landmark = next((l for l in dataset["landmarks"] if l["id"] == landmark_id), None)
    if not landmark:
        return {"recognised": False, "message": "Landmark not in dataset yet."}

    narrative = f"{landmark['name']} ({landmark['name_urdu']}) was built by {landmark['built_by']} in {landmark['year_built']} during the {landmark['period']} period. {landmark['description']}"

    return {
        "recognised":       True,
        "landmark_id":      landmark_id,
        "confidence":       round(confidence * 100, 1),
        "name":             landmark["name"],
        "name_urdu":        landmark["name_urdu"],
        "built_by":         landmark["built_by"],
        "year_built":       landmark["year_built"],
        "period":           landmark["period"],
        "coordinates":      landmark["coordinates"],
        "significance":     landmark["significance"],
        "narrative":        narrative,
        "reference_images": landmark["reference_images"]
    }
#uvicorn main:app --reload