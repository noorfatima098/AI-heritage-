import tempfile
import shutil
import os
import json
import chromadb
import open_clip
import torch
from fastapi.responses import FileResponse
from realesrgan import RealESRGANer
from basicsr.archs.rrdbnet_arch import RRDBNet
import cv2
from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import tf_keras
import numpy as np
from PIL import Image
from groq import Groq
from dotenv import load_dotenv

from generate_narrative import generate_narrative  # NEW — RAG narrative pipeline

load_dotenv()
app = FastAPI()

# Load model and dataset once at startup
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Base directory (backend/ folder)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load model and dataset once at startup
model = tf_keras.models.load_model(os.path.join(BASE_DIR, 'model', 'keras_model.h5'))
labels = open(os.path.join(BASE_DIR, 'model', 'labels.txt')).read().splitlines()
dataset = json.load(open(os.path.join(BASE_DIR, 'dataset', 'lahore_fort_dataset.json'), encoding='utf-8'))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ChromaDB setup
chroma_client = chromadb.PersistentClient(path=os.path.join(BASE_DIR, "vectordb"))
collection = chroma_client.get_or_create_collection("lahore_fort")

# CLIP model for vector search
clip_model, _, clip_preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='openai')
clip_model.eval()

def embed_image_clip(image_path):
    img = clip_preprocess(Image.open(image_path).convert("RGB")).unsqueeze(0)
    with torch.no_grad():
        return clip_model.encode_image(img).squeeze().tolist()

def confirm_with_chroma(image_path, cnn_landmark_id, cnn_confidence):
    if cnn_confidence > 0.85:
        return cnn_landmark_id  # CNN confident hai
    # CNN uncertain — ChromaDB se confirm karo
    query_vec = embed_image_clip(image_path)
    results = collection.query(query_embeddings=[query_vec], n_results=1)
    chroma_id = results["metadatas"][0][0]["landmark_id"]
    # Agar chroma bhi uncertain ho, CNN ka result use karo
    if chroma_id == "others":
        return cnn_landmark_id
    return chroma_id

rrdb = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
esrgan = RealESRGANer(
    scale=4,
    model_path=os.path.join(BASE_DIR, "weights", "RealESRGAN_x4plus.pth"),
    model=rrdb,
    tile=400
)
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
    landmark_id = confirm_with_chroma(tmp, landmark_id, confidence)
    os.remove(tmp)
    print(f"DEBUG: {landmark_id} = {confidence}")

    if landmark_id == "other" or confidence < 0.75:
        return {"recognised": False, "message": "Landmark not recognised. Try a clearer photo."}

    if confidence < 0.88:
        return {
        "recognised": True,
        "landmark_id": landmark_id,
        "confidence": round(confidence * 100, 1),
        "name": "Possibly " + (next((l["name"] for l in dataset["landmarks"] if l["id"] == landmark_id), landmark_id)),
        "name_urdu": next((l["name_urdu"] for l in dataset["landmarks"] if l["id"] == landmark_id), ""),
        "built_by": next((l["built_by"] for l in dataset["landmarks"] if l["id"] == landmark_id), ""),
        "year_built": next((l["year_built"] for l in dataset["landmarks"] if l["id"] == landmark_id), ""),
        "period": next((l["period"] for l in dataset["landmarks"] if l["id"] == landmark_id), ""),
        "coordinates": next((l["coordinates"] for l in dataset["landmarks"] if l["id"] == landmark_id), {}),
        "significance": "Exact monument unclear from this angle — try a closer or more distinctive shot.",
        "narrative": "This appears to be in the " + (next((l["name"] for l in dataset["landmarks"] if l["id"] == landmark_id), landmark_id)) + " area of Lahore Fort. For a more accurate identification, please try uploading a photo showing a distinctive architectural feature such as tile-work, marble carvings, or a unique structural element.",
        "reference_images": next((l["reference_images"] for l in dataset["landmarks"] if l["id"] == landmark_id), [])
    }

    landmark = next((l for l in dataset["landmarks"] if l["id"] == landmark_id), None)
    if not landmark:
        return {"recognised": False, "message": "Landmark not in dataset yet."}

    # --- NEW: RAG-based narrative (retrieval from the 30-landmark PDF corpus + Groq) ---
    # Falls back to the old one-line dataset.json prompt if this landmark_id
    # isn't in the PDF corpus yet (e.g. not ingested, or a genuine gap),
    # so /identify never breaks even if a landmark is missing from vectordb.
    try:
        narrative = generate_narrative(
            landmark_id,
            chroma_client=chroma_client,
            groq_client=groq_client,
        )
    except ValueError as e:
        print(f"DEBUG: RAG narrative unavailable for '{landmark_id}' ({e}); falling back to dataset.json prompt")
        prompt = f"""Write 1 engaging paragraph about {landmark['name']} ({landmark['name_urdu']}) for a heritage app visitor.
        Built by: {landmark['built_by']} | Year: {landmark['year_built']} | Period: {landmark['period']}
        Details: {landmark['description']}
        Significance: {landmark['significance']}"""

        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
        )
        narrative = chat_completion.choices[0].message.content
    # --- END NEW ---

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
    
@app.post("/enhance")
async def enhance(file: UploadFile):
    tmp_in  = os.path.join(tempfile.gettempdir(), "in_" + file.filename)
    tmp_out = os.path.join(tempfile.gettempdir(), "out_" + file.filename)

    with open(tmp_in, "wb") as f:
        shutil.copyfileobj(file.file, f)

    img = cv2.imread(tmp_in, cv2.IMREAD_UNCHANGED)
    enhanced, _ = esrgan.enhance(img, outscale=4)
    cv2.imwrite(tmp_out, enhanced)

    return FileResponse(tmp_out, media_type="image/jpeg")
@app.get("/landmarks")
async def get_landmarks():
    return {"landmarks": dataset["landmarks"]}
#cd "C:\Users\User\OneDrive\Desktop\python\AI heritage\AI-heritage-\backend"
# uvicorn main:app --reload