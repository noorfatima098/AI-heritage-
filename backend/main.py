import tempfile
import shutil
import os
import json
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
    os.remove(tmp)
    print(f"DEBUG: {landmark_id} = {confidence}")

    if landmark_id == "other" or confidence < 0.75:
        return {"recognised": False, "message": "Landmark not recognised. Try a clearer photo."}

    landmark = next((l for l in dataset["landmarks"] if l["id"] == landmark_id), None)
    if not landmark:
        return {"recognised": False, "message": "Landmark not in dataset yet."}

    prompt = f"""Write 2 engaging paragraphs about {landmark['name']} ({landmark['name_urdu']}) for a heritage app visitor.
    Built by: {landmark['built_by']} | Year: {landmark['year_built']} | Period: {landmark['period']}
    Details: {landmark['description']}
    Significance: {landmark['significance']}"""


    chat_completion = groq_client.chat.completions.create(
    messages=[{"role": "user", "content": prompt}],
    model="llama-3.3-70b-versatile",
)
    narrative = chat_completion.choices[0].message.content

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
#cd "OneDrive\Desktop\python\AI heritage\AI-heritage-\backend"
# uvicorn main:app --reload