import chromadb
import open_clip
import torch
from PIL import Image
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "..", "assets")

# CLIP model load karo
print("Loading CLIP model...")
clip_model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='openai')
clip_model.eval()

# ChromaDB client
client = chromadb.PersistentClient(path=os.path.join(BASE_DIR, "vectordb"))
collection = client.get_or_create_collection("lahore_fort")

def embed_image(path):
    img = preprocess(Image.open(path).convert("RGB")).unsqueeze(0)
    with torch.no_grad():
        vector = clip_model.encode_image(img).squeeze().tolist()
    return vector

# Saare landmark folders index karo
count = 0
errors = 0
for landmark_id in os.listdir(ASSETS_DIR):
    folder = os.path.join(ASSETS_DIR, landmark_id)
    if not os.path.isdir(folder):
        continue
    if landmark_id == "others":
        continue  # others class skip karo
    
    print(f"\nIndexing: {landmark_id}")
    for fname in os.listdir(folder):
        if fname.lower().endswith((".jpg", ".jpeg", ".png")):
            path = os.path.join(folder, fname)
            try:
                vector = embed_image(path)
                collection.add(
                    embeddings=[vector],
                    ids=[f"{landmark_id}_{fname}"],
                    metadatas=[{"landmark_id": landmark_id}]
                )
                count += 1
            except Exception as e:
                errors += 1
                print(f"  Skip {fname}: {e}")

print(f"\n✅ Total {count} images indexed!")
print(f"❌ Errors: {errors}")