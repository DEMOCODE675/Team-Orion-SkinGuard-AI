import streamlit as st
import pyrebase
import os
from dotenv import load_dotenv
from datetime import datetime
import firebase_client  # new helper module

load_dotenv()  # load variables from .env

# Cache Firebase instance to avoid re-initialization
@st.cache_resource
def _get_firebase():
    config = {
        "apiKey": os.getenv("FIREBASE_API_KEY", ""),
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN", ""),
        "projectId": os.getenv("FIREBASE_PROJECT_ID", ""),
        "databaseURL": os.getenv("FIREBASE_DB_URL", ""),
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET", ""),
    }
    if not all(config.values()):
        st.error("❌ Firebase config incomplete. Check your .env file.")
        st.stop()
    return pyrebase.initialize_app(config)

def _get_auth():
    firebase = _get_firebase()
    return firebase.auth()

# Restore session at import (if available)
try:
    sess = firebase_client.load_session()
    if sess and isinstance(sess, dict):
        if "localId" in sess and "idToken" in sess and "email" in sess:
            # ensure streamlit session_state keys exist and set them
            try:
                if "authenticated" not in st.session_state:
                    st.session_state.authenticated = False
                if "user" not in st.session_state:
                    st.session_state.user = None
                st.session_state.authenticated = True
                st.session_state.user = sess.get("email")
                st.session_state.localId = sess.get("localId")
                st.session_state.idToken = sess.get("idToken")
            except Exception:
                pass
except Exception:
    pass

def login_ui():
    st.subheader("🔐 Login")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        if not email or not password:
            st.error("Email and password required")
            return
        try:
            fb_auth = _get_auth()
            user = fb_auth.sign_in_with_email_and_password(email, password)
            st.session_state.authenticated = True
            st.session_state.user = email
            st.session_state.idToken = user.get("idToken")
            st.session_state.localId = user.get("localId")
            # persist last login in DB
            try:
                firebase_client.save_user_profile(
                    st.session_state.localId,
                    {"email": email, "last_login": datetime.utcnow().isoformat()}
                )
            except Exception:
                pass
            # save local session so reload keeps user signed in
            try:
                firebase_client.save_session({
                    "localId": st.session_state.localId,
                    "idToken": st.session_state.idToken,
                    "email": email
                })
            except Exception:
                pass
            st.success("Login successful")
            st.rerun()
        except Exception:
            st.error("Login failed. Check credentials.")

def signup_ui():
    st.subheader("📝 Sign Up")
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_password")
    confirm = st.text_input("Confirm Password", type="password", key="signup_confirm")

    if st.button("Create Account"):
        if not email or not password:
            st.error("Email and password required")
            return
        if password != confirm:
            st.error("Passwords do not match")
            return
        if len(password) < 6:
            st.error("Password must be at least 6 characters")
            return
        try:
            fb_auth = _get_auth()
            fb_auth.create_user_with_email_and_password(email, password)
            # sign in immediately
            user = fb_auth.sign_in_with_email_and_password(email, password)
            st.session_state.authenticated = True
            st.session_state.user = email
            st.session_state.idToken = user.get("idToken")
            st.session_state.localId = user.get("localId")
            # persist profile in DB
            try:
                firebase_client.save_user_profile(
                    st.session_state.localId,
                    {"email": email, "created_at": datetime.utcnow().isoformat()}
                )
            except Exception:
                pass
            # save local session
            try:
                firebase_client.save_session({
                    "localId": st.session_state.localId,
                    "idToken": st.session_state.idToken,
                    "email": email
                })
            except Exception:
                pass
            st.success("Account created and logged in.")
            st.rerun()
        except Exception:
            st.error("Signup failed. The email may already be in use.")
