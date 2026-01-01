# Setup Guide — SkinGuard AI

1. Prerequisites

- Python 3.9+
- git
- Firebase account (console.firebase.google.com)

2. Repository layout (important paths)

- Frontend: frontend/streamlit_app.py
- Frontend auth + helpers: frontend/auth.py, frontend/firebase_client.py
- Backend: backend/app.py
- Env file: c:\Users\priya\Music\AI-cancer\.env
- Local session file: frontend/.session.json (auto-created)

3. Firebase setup (console)

- Create project.
- Authentication → Sign-in method → Enable Email/Password.
- Realtime Database (or Firestore) → create database (start in test mode for dev).
- Storage → create bucket.
- Project Settings → add Web App (optional) to get apiKey/authDomain.
- (Optional) Service account → generate private key if you plan to use Admin SDK on server.

4. .env (create at project root)

- Add these keys (fill values from Firebase):
  FIREBASE_API_KEY=your-firebase-api-key
  FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
  FIREBASE_PROJECT_ID=your-project-id
  FIREBASE_DB_URL=https://your-project.firebaseio.com
  FIREBASE_STORAGE_BUCKET=your-project.appspot.com
  # optional
  OPENAI_API_KEY=your-openai-key
  MODEL_PATH=backend/model.h5

5. .gitignore (recommended)

- Add:
  .env
  frontend/firebase_creds.json
  frontend/.session.json
  \*.h5
  venv/
  **pycache**/

6. Python dependencies

- Create venv and install:
  python -m venv .venv
  .venv\Scripts\activate (Windows)
  pip install --upgrade pip
  pip install streamlit pyrebase4 python-dotenv firebase-admin requests pillow fastapi uvicorn tensorflow

7. Configure Firebase DB & Storage rules (dev)

- Realtime DB (rules) allow authenticated reads/writes:
  {
  "rules": {
  ".read": "auth != null",
  ".write": "auth != null"
  }
  }
- Storage: for dev, allow authenticated uploads. Harden for prod.

8. Model

- Place your TF model at the path specified by MODEL_PATH (.env) or backend/model.h5
- If no model, create a placeholder or mock endpoint for testing.

9. Running locally

- Start backend:
  cd backend
  uvicorn app:app --reload --port 8000
- Start frontend:
  cd frontend
  streamlit run streamlit_app.py

10. Test flow

- Open Streamlit UI → Sign Up (sidebar) → Log In.
- Upload or take a picture → Analyze Image.
- Confirm record appears in Realtime Database under `analyses/<localId>` with optional `image_url`.

11. Notes & troubleshooting

- If Firebase auth fails: confirm FIREBASE_API_KEY and authDomain in .env.
- If storage upload fails: check storage rules and provide idToken for authenticated uploads.
- Persisted session stored in frontend/.session.json — remove to force logout.
- For production: use HTTPS, secure database rules, and avoid storing secrets in repo.

12. Optional: Admin server usage

- Use Firebase Admin SDK (service account JSON) on backend for privileged tasks (do NOT include service account in frontend).
- Place service account at frontend/firebase_creds.json or backend/firebase_admin.json and add to .gitignore.

End of setup.
