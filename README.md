# SkinGuard AI

> **AI-assisted skin lesion screening for educational use — not a medical diagnosis.**

SkinGuard AI is a web application built by **Team Orion** that uses a TensorFlow image-classification model to provide an initial benign/malignant prediction for an uploaded or camera-captured skin image. The app combines a Streamlit interface, a FastAPI inference service, Firebase authentication and storage, and optional AI-generated explanations.

## What it does

- Authenticates users with Firebase Email/Password authentication
- Accepts JPG and PNG uploads or a photo from the device camera
- Classifies an image as `benign` or `malignant`
- Returns a confidence score and plain-language explanation
- Saves analysis results and optional image URLs to Firebase
- Provides a Google Maps link for nearby dermatologists
- Exposes a lightweight FastAPI endpoint for model inference

## Important medical disclaimer

SkinGuard AI is a research and educational prototype. Its output is an AI prediction, not a diagnosis, medical advice, or a substitute for examination by a qualified clinician. Model confidence does not indicate clinical certainty. Always consult a dermatologist, especially for lesions that change in size, shape, colour, or appearance, or whenever you are concerned.

## Architecture

```text
User
  |
  v
Streamlit frontend ── Firebase Auth / Storage / Realtime Database
  |
  | multipart image upload
  v
FastAPI backend ── TensorFlow/Keras model
  |
  v
Prediction + confidence + explanation
```

### Project structure

```text
.
├── backend/
│   ├── app.py                 # FastAPI API and inference pipeline
│   ├── config.py              # Model path, image size, class names
│   ├── model/skinguard.keras  # Trained Keras model
│   ├── requirements.txt
│   └── Procfile               # Deployment command
├── frontend/
│   ├── streamlit_app.py       # User interface
│   ├── auth.py                 # Firebase login and signup UI
│   ├── firebase_client.py      # Firebase persistence helpers
│   └── requirements.txt
├── train_model.py              # EfficientNet-based training script
├── split_resize.py             # Dataset preparation helper
├── test_backend.py             # Backend tests
├── FIREBASE_SETUP.md           # Firebase configuration walkthrough
└── setup.md                    # Expanded local setup notes
```

## Quick start

### Prerequisites

- Python 3.9 or newer (the included deployment runtime uses Python 3.13)
- Git
- A Firebase project with Email/Password Authentication enabled
- A local TensorFlow/Keras model at `backend/model/skinguard.keras`

### 1. Clone the repository

```bash
git clone https://github.com/DEMOCODE675/Team-Orion-SkinGuard-AI.git
cd Team-Orion-SkinGuard-AI
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv

# macOS/Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
```

The frontend has a separate requirements file if you prefer a dedicated environment:

```bash
python -m pip install -r frontend/requirements.txt
```

### 4. Configure environment variables

Copy the example file and fill in your Firebase project values:

```bash
cp .env.example .env
```

On Windows, copy `.env.example` to `.env` manually or use `Copy-Item .env.example .env`.

Required frontend settings include:

```dotenv
FIREBASE_API_KEY=your-firebase-api-key
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_DB_URL=https://your-project.firebaseio.com
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
```

Optional settings include `OPENAI_API_KEY` for generated explanations and `FIREBASE_SERVICE_ACCOUNT` for server-side Firebase administration. Never commit `.env`, service-account JSON, tokens, or other credentials.

See [FIREBASE_SETUP.md](FIREBASE_SETUP.md) for Firebase console configuration and security-rule guidance.

### 5. Start the backend

From the repository root:

```bash
cd backend
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The backend health check is available at [http://localhost:8000/](http://localhost:8000/). The prediction endpoint accepts a multipart image at `POST /predict`.

### 6. Start the frontend

In a second terminal:

```bash
cd frontend
streamlit run streamlit_app.py
```

Sign up or log in, select an image source, upload or capture an image, and choose **Analyze Image**.

> The current Streamlit client uses the deployed backend URL configured in `frontend/streamlit_app.py`. For local development, point `BACKEND_URL` to `http://localhost:8000`.

## API

### `GET /`

Returns a simple service health response:

```json
{"status":"SkinGuard AI backend running"}
```

### `POST /predict`

Upload a JPG or PNG image using the `file` multipart field:

```bash
curl -X POST http://localhost:8000/predict \
  -F "file=@path/to/lesion.jpg"
```

Example response:

```json
{
  "prediction": "benign",
  "confidence": 87.42,
  "ai_explanation": "..."
}
```

## Model and dataset

The included inference configuration uses a 224×224 input and the classes `benign` and `malignant`. `train_model.py` documents an EfficientNetB3 training workflow with augmentation, class weighting, early stopping, checkpointing, and fine-tuning.

The project references the [HAM10000 skin lesion dataset](https://www.kaggle.com/datasets/kmader/skin-cancer-mnist-ham10000). The dataset is not included in this repository. Review its terms and obtain it through the official source before training.

To train a model using the documented script, arrange data as:

```text
dataset/
├── train/
│   ├── benign/
│   └── malignant/
└── validation/
    ├── benign/
    └── malignant/
```

Then run:

```bash
python train_model.py
```

## Deployment

The backend includes a `Procfile` for platforms that provide a `$PORT` environment variable:

```text
web: uvicorn app:app --host 0.0.0.0 --port $PORT
```

For production deployment, configure HTTPS, restrict CORS to trusted origins, enforce authenticated Firebase database and storage rules, validate uploads and file sizes, and keep all credentials outside source control.

## Testing

Run the available backend tests with:

```bash
python -m pytest
```

## Contributing

1. Create a feature branch.
2. Keep secrets and private medical data out of commits.
3. Add or update tests for behavior changes.
4. Update documentation when setup or API behavior changes.
5. Open a pull request with a concise description and verification steps.

## License

No license file is currently included. Add an explicit license before redistributing this project or accepting external contributions under defined reuse terms.

## Team

Built by **Team Orion** as an AI-assisted skin screening prototype.
