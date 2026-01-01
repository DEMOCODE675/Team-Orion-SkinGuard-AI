import os
import json
import tempfile
import pyrebase
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SESSION_FILE = os.path.join("frontend", ".session.json")

@st.cache_resource
def _get_firebase():
    config = {
        "apiKey": os.getenv("FIREBASE_API_KEY", ""),
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN", ""),
        "projectId": os.getenv("FIREBASE_PROJECT_ID", ""),
        "databaseURL": os.getenv("FIREBASE_DB_URL", ""),
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET", ""),
    }
    # Return initialized app (will raise if config invalid)
    return pyrebase.initialize_app(config)

def get_db():
    return _get_firebase().database()

def get_storage():
    return _get_firebase().storage()

def save_user_profile(local_id, profile: dict):
    try:
        get_db().child("users").child(local_id).update(profile)
    except Exception:
        pass

def save_analysis_result(local_id, result: dict):
    try:
        if local_id:
            get_db().child("analyses").child(local_id).push(result)
        else:
            get_db().child("analyses").push(result)
    except Exception:
        pass

def upload_image(local_id, image_bytes: bytes, filename: str, id_token: str = None):
    """Upload image bytes to Firebase Storage and return a download URL or None."""
    try:
        storage = get_storage()
        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
        user_part = local_id if local_id else "anonymous"
        path = f"analyses/{user_part}/{ts}_{filename}"
        # write to temp file then upload
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
            tmp.write(image_bytes)
            tmp.flush()
            tmp_name = tmp.name
        try:
            if id_token:
                storage.child(path).put(tmp_name, id_token)
            else:
                storage.child(path).put(tmp_name)
            try:
                url = storage.child(path).get_url(None)
            except Exception:
                url = None
        finally:
            try:
                os.remove(tmp_name)
            except Exception:
                pass
        return url
    except Exception:
        return None

def save_session(session: dict):
    try:
        os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump(session, f)
    except Exception:
        pass

def load_session():
    try:
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return None

def clear_session():
    try:
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
    except Exception:
        pass