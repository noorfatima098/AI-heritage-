import os
import cv2
import numpy as np
from PIL import Image, ImageEnhance
import random

ASSETS = r"C:\Users\User\OneDrive\Desktop\python\AI heritage\AI-heritage-\assets"
TARGET = 70  # minimum photos per class

def augment_image(img):
    """Random augmentation — flip, rotate, brightness"""
    aug = img.copy()
    # Random horizontal flip
    if random.random() > 0.5:
        aug = cv2.flip(aug, 1)
    # Random rotation (-15 to +15 degrees)
    angle = random.uniform(-15, 15)
    h, w = aug.shape[:2]
    M = cv2.getRotationMatrix2D((w//2, h//2), angle, 1.0)
    aug = cv2.warpAffine(aug, M, (w, h))
    # Random brightness
    pil = Image.fromarray(cv2.cvtColor(aug, cv2.COLOR_BGR2RGB))
    factor = random.uniform(0.7, 1.3)
    pil = ImageEnhance.Brightness(pil).enhance(factor)
    aug = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
    return aug

for landmark in os.listdir(ASSETS):
    folder = os.path.join(ASSETS, landmark)
    if not os.path.isdir(folder):
        continue
    
    images = [f for f in os.listdir(folder) 
              if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    count = len(images)
    
    if count >= TARGET:
        print(f"✅ {landmark}: {count} — skip")
        continue
    
    needed = TARGET - count
    print(f"⚠️ {landmark}: {count} → adding {needed} augmented images...")
    
    generated = 0
    while generated < needed:
        # Pick a random existing image
        src = random.choice(images)
        img = cv2.imread(os.path.join(folder, src))
        if img is None:
            continue
        aug = augment_image(img)
        # Save with aug_ prefix
        out_name = f"aug_{generated+1:03d}_{src}"
        cv2.imwrite(os.path.join(folder, out_name), aug)
        generated += 1
    
    print(f"   ✓ Done — {landmark} now has {TARGET} images")

print("\n✅ Augmentation complete!")