# backend/app.py

import os
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")

import io
import numpy as np
from PIL import Image
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import tensorflow as tf

# Optional OpenAI (safe fallback if not installed)
try:
    from openai import OpenAI
except Exception:
    OpenAI = None

from dotenv import load_dotenv
load_dotenv()
from config import IMG_SIZE, CLASS_NAMES, MODEL_PATH

# =====================
# LOAD MODEL
# =====================
model = tf.keras.models.load_model(MODEL_PATH)

# =====================
# OPENAI SETUP (OPTIONAL)
# =====================
openai_client = None
if OpenAI and os.getenv("OPENAI_API_KEY"):
    try:
        openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    except Exception:
        openai_client = None

# =====================
# FASTAPI APP
# =====================
app = FastAPI(title="SkinGuard AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================
# IMAGE PREPROCESSING
# =====================
def preprocess_image(image: Image.Image):
    image = image.convert("RGB")
    image = image.resize((IMG_SIZE, IMG_SIZE))
    arr = np.array(image) / 255.0
    arr = np.expand_dims(arr, axis=0)
    return arr

# =====================
# AI EXPLANATION LOGIC
# =====================
def generate_ai_explanation(label, confidence):
    # Reason hint for variation
    if label == "benign" and confidence > 0.75:
        reason = "uniform color and smooth, well-defined borders"
    elif label == "malignant" and confidence > 0.75:
        reason = "irregular borders, color variation, or asymmetry"
    else:
        reason = "mixed visual patterns that make classification uncertain"

    # OpenAI available
    if openai_client:
        try:
            prompt = f"""
    You are an AI dermatology assistant. You are not a doctor and cannot provide medical diagnosis.

    The AI model analyzed an image and predicted:
    - Condition: {label}
    - Confidence: {confidence:.2f}%

    Visual cues observed: {reason}

    Explain in simple, clear language for a general user:
    1. What patterns or features the AI noticed in the image
    2. What these observations might indicate
    3. Recommended next steps or precautions the user can take (e.g., consult a dermatologist)

    End with a short, clear disclaimer emphasizing:
    - This is an AI-based suggestion only
    - It is not a substitute for professional medical advice
    """


            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6
            )

            return response.choices[0].message.content

        except Exception:
            pass

    # Fallback explanation (ALWAYS WORKS)
    return (
        f"The model predicted '{label}' with confidence {confidence:.2f}. "
        f"This decision may be influenced by {reason}. "
        "If the lesion changes in size, color, or shape, consult a qualified dermatologist. "
        "This explanation is for educational purposes only and is not a medical diagnosis."
    )

# =====================
# PREDICTION ENDPOINT
# =====================
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes))

    input_tensor = preprocess_image(image)
    pred = model.predict(input_tensor)[0][0]

    label = CLASS_NAMES[int(pred > 0.5)]
    confidence = float(pred if label == "malignant" else 1 - pred)

    explanation = generate_ai_explanation(label, confidence)

    return {
        "prediction": label,
        "confidence": round(confidence * 100, 2),
        "ai_explanation": explanation
    }

# =====================
# HEALTH CHECK
# =====================
@app.get("/")
def root():
    return {"status": "SkinGuard AI backend running"}
