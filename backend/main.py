import tempfile
import shutil
import os
import json
import math
import chromadb
import open_clip
import torch
from fastapi.responses import FileResponse
from realesrgan import RealESRGANer
from basicsr.archs.rrdbnet_arch import RRDBNet
import cv2
from fastapi import FastAPI, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import tf_keras
import numpy as np
from PIL import Image
from groq import Groq
from dotenv import load_dotenv

from generate_narrative import generate_narrative  # NEW — RAG narrative pipeline

load_dotenv()
app = FastAPI()

# CORS — defaults to "*" for local dev. For a real deployment, set
# ALLOWED_ORIGINS in .env to a comma-separated list (e.g.
# "https://your-frontend.com,http://localhost:3000") so any site can't
# call this API from a browser.
_allowed_origins = os.getenv("ALLOWED_ORIGINS", "*")
_allowed_origins = [o.strip() for o in _allowed_origins.split(",")] if _allowed_origins != "*" else ["*"]
app.add_middleware(CORSMiddleware, allow_origins=_allowed_origins, allow_methods=["*"], allow_headers=["*"])

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

# CLIP model for vector search — lazy-loaded on first use, not at startup,
# so app boot doesn't pay this cost when a session never hits the CNN's
# low-confidence fallback path.
_clip_model = None
_clip_preprocess = None

def _get_clip():
    global _clip_model, _clip_preprocess
    if _clip_model is None:
        _clip_model, _, _clip_preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='openai')
        _clip_model.eval()
    return _clip_model, _clip_preprocess

def embed_image_clip(image_path):
    clip_model, clip_preprocess = _get_clip()
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

# Real-ESRGAN — lazy-loaded on first /enhance call, not at startup, since
# it's a heavy model (weights file + GPU/CPU init) that a session may
# never touch.
_esrgan = None

def _get_esrgan():
    global _esrgan
    if _esrgan is None:
        rrdb = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
        _esrgan = RealESRGANer(
            scale=4,
            model_path=os.path.join(BASE_DIR, "weights", "RealESRGAN_x4plus.pth"),
            model=rrdb,
            tile=400
        )
    return _esrgan

def classify(image_path, top_k=3):
    """Returns top_k (landmark_id, confidence) tuples, sorted by confidence desc."""
    img  = Image.open(image_path).resize((224, 224)).convert("RGB")
    arr  = np.array(img, dtype=np.float32) / 255.0
    arr  = np.expand_dims(arr, axis=0)
    pred = model.predict(arr)[0]
    top_idx = np.argsort(pred)[::-1][:top_k]
    return [(labels[i].split(" ", 1)[-1].lower().replace(" ", "-"), float(pred[i])) for i in top_idx]

def haversine_m(lat1, lng1, lat2, lng2):
    """Distance in meters between two lat/lng points."""
    R = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))

def rerank_with_location(top_preds, user_lat, user_lng, decay_m=40):
    """
    Re-ranks the CNN's own top-3 shortlist using proximity to the user's
    GPS location — helps break ties between visually similar (e.g. red
    sandstone) buildings that are far enough apart to be distinguishable
    by GPS. Only ever picks among what the CNN already considered
    plausible; GPS can boost a candidate's score by up to 40%, not
    override the CNN outright (phone GPS near stone walls can drift
    15-30m, so it's a nudge, not a verdict).
    """
    scored = []
    for landmark_id, conf in top_preds:
        landmark = next((l for l in dataset["landmarks"] if l["id"] == landmark_id), None)
        coords = landmark.get("coordinates") if landmark else None
        if not coords:
            scored.append((landmark_id, conf, conf))
            continue
        dist = haversine_m(user_lat, user_lng, coords["lat"], coords["lng"])
        proximity_weight = math.exp(-dist / decay_m)
        combined = conf * (0.6 + 0.4 * proximity_weight)
        scored.append((landmark_id, conf, combined))
    scored.sort(key=lambda x: x[2], reverse=True)
    best_id, best_cnn_conf, _ = scored[0]
    return best_id, best_cnn_conf

@app.post("/identify")
async def identify(file: UploadFile, lat: float = Form(None), lng: float = Form(None)):
    tmp = os.path.join(tempfile.gettempdir(), file.filename)
    with open(tmp, "wb") as f:
        shutil.copyfileobj(file.file, f)
    # GPS-ONLY check — CNN se pehle
    # Agar user 30m ke andar hai kisi bhi landmark ke — seedha identify karo
    if lat is not None and lng is not None:
        nearest = None
        min_dist = float('inf')
        for l in dataset["landmarks"]:
            dist = haversine_m(lat, lng, l["coordinates"]["lat"], l["coordinates"]["lng"])
            if dist < min_dist:
                min_dist = dist
                nearest = l
        
        if min_dist < 30 and nearest:
            os.remove(tmp)
            print(f"DEBUG: GPS identified — {nearest['id']} at {min_dist:.1f}m")
            try:
                narrative = generate_narrative(nearest["id"], chroma_client=chroma_client, groq_client=groq_client)
            except ValueError:
                narrative = f"{nearest['name']} is a significant heritage monument within Lahore Fort. {nearest['description']}"
            return {
                "recognised":       True,
                "landmark_id":      nearest["id"],
                "confidence":       99.0,
                "name":             nearest["name"],
                "name_urdu":        nearest["name_urdu"],
                "built_by":         nearest["built_by"],
                "year_built":       nearest["year_built"],
                "period":           nearest["period"],
                "coordinates":      nearest["coordinates"],
                "significance":     nearest["significance"],
                "narrative":        narrative,
                "reference_images": nearest["reference_images"],
                "identified_by":    "GPS"
            }

    top_preds = classify(tmp)
    landmark_id, confidence = top_preds[0]

    if lat is not None and lng is not None and confidence < 0.85:
        # CNN is unsure — use GPS to re-rank within its own top-3 shortlist
        # before falling back to the CLIP/ChromaDB confirm.
        landmark_id, confidence = rerank_with_location(top_preds, lat, lng)
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

    try:
        with open(tmp_in, "wb") as f:
            shutil.copyfileobj(file.file, f)

        img = cv2.imread(tmp_in, cv2.IMREAD_UNCHANGED)
        if img is None:
            # Not a valid/decodable image — corrupt file, wrong format, etc.
            raise HTTPException(status_code=400, detail="Could not read uploaded file as an image. Try a JPG or PNG.")

        try:
            enhanced, _ = _get_esrgan().enhance(img, outscale=4)
        except Exception as e:
            print(f"DEBUG: ESRGAN enhance failed: {e}")
            raise HTTPException(status_code=500, detail="Image enhancement failed. Try a smaller or different image.")

        cv2.imwrite(tmp_out, enhanced)
        return FileResponse(tmp_out, media_type="image/jpeg")
    finally:
        # Always clean up temp input, whether we succeeded, failed, or raised.
        if os.path.exists(tmp_in):
            os.remove(tmp_in)
@app.get("/landmarks")
async def get_landmarks():
    return {"landmarks": dataset["landmarks"]}
#cd "C:\Users\User\OneDrive\Desktop\python\AI heritage\AI-heritage-\backend"
# uvicorn main:app --reload