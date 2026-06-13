from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import tensorflow as tf
import numpy as np
from PIL import Image
import anthropic, json, shutil, os

app = FastAPI()

# Allow frontend to connect
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Load model and dataset once at startup
model = tf.keras.models.load_model('backend/model/keras_model.h5')
labels  = open('backend/model/labels.txt').read().splitlines()
dataset = json.load(open('backend/dataset/lahore_fort_dataset.json', encoding='utf-8'))
claude  = anthropic.Anthropic(api_key="YOUR_API_KEY_HERE")

def classify(image_path):
    img  = Image.open(image_path).resize((224, 224)).convert("RGB")
    arr  = np.array(img, dtype=np.float32) / 255.0
    arr  = np.expand_dims(arr, axis=0)
    pred = model.predict(arr)[0]
    idx  = np.argmax(pred)
    return labels[idx].split(" ", 1)[-1].lower().replace(" ", "-"), float(pred[idx])

@app.post("/identify")
async def identify(file: UploadFile):
    # Save uploaded image temporarily
    tmp = f"/tmp/{file.filename}"
    with open(tmp, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Classify
    landmark_id, confidence = classify(tmp)
    os.remove(tmp)

    # If not recognised or low confidence
    if landmark_id == "other" or confidence < 0.75:
        return {"recognised": False, "message": "Landmark not recognised. Try a clearer photo."}

    # Look up JSON dataset
    landmark = next((l for l in dataset["landmarks"] if l["id"] == landmark_id), None)
    if not landmark:
        return {"recognised": False, "message": "Landmark not in dataset yet."}

    # Generate narrative with Claude
    prompt = f"""You are a heritage guide for Lahore Fort.
Write 2 engaging paragraphs about {landmark['name']} ({landmark['name_urdu']}).
Built by: {landmark['built_by']} | Year: {landmark['year_built']} | Period: {landmark['period']}
Details: {landmark['description']}
Significance: {landmark['significance']}
Keep it warm, informative, and suitable for a heritage app visitor."""

    response = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    return {
        "recognised":        True,
        "landmark_id":       landmark_id,
        "confidence":        round(confidence * 100, 1),
        "name":              landmark["name"],
        "name_urdu":         landmark["name_urdu"],
        "built_by":          landmark["built_by"],
        "year_built":        landmark["year_built"],
        "period":            landmark["period"],
        "coordinates":       landmark["coordinates"],
        "significance":      landmark["significance"],
        "narrative":         response.content[0].text,
        "reference_images":  landmark["reference_images"]
    }