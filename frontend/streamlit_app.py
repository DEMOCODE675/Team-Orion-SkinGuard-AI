import streamlit as st
import requests
from PIL import Image
import io
import auth
import firebase_client  # new import

# ======================
# Config
# ======================
BACKEND_URL = "https://team-orion-skinguard-ai.onrender.com/analyze"


logo = Image.open("assets/logo.png")

col1, col2 = st.columns([1, 4])

with col1:
    st.image(logo, width=120)

with col2:
    st.markdown(
        """
        <h1 style='margin-bottom:0;'>SkinGuard AI</h1>
        <p style='font-size:18px;color:gray;'>by Team Orion</p>
        """,
        unsafe_allow_html=True
    )
st.set_page_config(page_title="SkinGuard AI", layout="centered")

st.write("AI-powered skin lesion analysis with nearby dermatologist support")

# Persistent state for results so UI doesn't lose data on rerun
if "result" not in st.session_state:
    st.session_state.result = None
if "city" not in st.session_state:
    st.session_state.city = ""

# ----------------------
# Authentication (Firebase)
# ----------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None

with st.sidebar:
    if not st.session_state.authenticated:
     if not st.session_state.authenticated:
        mode = st.radio("", ["Login", "Sign Up"])
        if mode == "Login":
            auth.login_ui()
        else:
            auth.signup_ui()
    else:
        st.write(f"Signed in as: {st.session_state.user}")
        if st.button("Logout"):
            auth.logout_user()
            st.rerun()

if not st.session_state.authenticated:
    st.info("Please login or sign up using the sidebar to use the app.")
    st.stop()

# ======================
# Image Input Section
# ======================
st.subheader("Choose Image Source")

image_source = st.radio(
    "Select image input method:",
    ("Upload Image", "Use Camera")
)

image = None
uploaded_bytes = None

if image_source == "Upload Image":
    uploaded_file = st.file_uploader(
        "Upload skin image (JPG / PNG)",
        type=["jpg", "jpeg", "png"]
    )
    if uploaded_file:
        image = Image.open(uploaded_file)
        uploaded_bytes = uploaded_file.getvalue()

elif image_source == "Use Camera":
    camera_file = st.camera_input("Take a picture")
    if camera_file:
        image = Image.open(camera_file)
        uploaded_bytes = camera_file.getvalue()

# ======================
# Image Preview
# ======================
if image:
    st.image(image, caption="Selected Image", use_column_width=True)

# ======================
# Analyze Button
# ======================
result = None

if image and st.button("Analyze Image"):
    with st.spinner("Analyzing image with AI..."):
        try:
            files = {
                "file": ("image.jpg", uploaded_bytes, "image/jpeg")
            }

            response = requests.post(BACKEND_URL, files=files)

            if response.status_code == 200:
                resp = response.json()
                st.session_state.result = resp
                result = resp

                # upload image to Firebase Storage and persist analysis with image_url
                try:
                    # prefer using stored filename from uploader if available
                    filename = getattr(uploaded_file, "name", "image.jpg") if 'uploaded_file' in locals() and uploaded_file else "image.jpg"
                    image_url = firebase_client.upload_image(
                        st.session_state.get("localId"),
                        uploaded_bytes,
                        filename,
                        st.session_state.get("idToken")
                    )
                    record = resp.copy()
                    record["timestamp"] = __import__("datetime").datetime.utcnow().isoformat()
                    if image_url:
                        record["image_url"] = image_url
                    firebase_client.save_analysis_result(st.session_state.get("localId"), record)
                except Exception:
                    pass

                st.success("Analysis Complete ✅")
            else:
                st.error("Backend error. Please try again.")

        except Exception as e:
            st.error(f"Connection error: {e}")

# ======================
# Results Section
# ======================
if st.session_state.result:
    result = st.session_state.result
    st.metric(
        label="Prediction",
        value=result["prediction"].capitalize()
    )

    st.metric(
        label="Confidence",
        value=f'{result["confidence"]}%'
    )

    st.subheader("AI Explanation")
    st.write(result["ai_explanation"])

    st.warning(
        "⚠️ **Disclaimer:** This result is NOT a medical diagnosis. "
        "Please consult a qualified dermatologist for professional advice."
    )

    st.divider()

    # ======================
    # AI Dermatologist Advice
    # ======================
    st.subheader("🤖 AI Dermatologist Advice")

    if result["prediction"] == "malignant":
        st.warning(
            "⚠️ The AI strongly recommends consulting a dermatologist as soon as possible. "
            "Early medical evaluation can be critical."
        )
    else:
        st.success(
            "✅ The lesion appears low-risk. However, regular monitoring is advised. "
            "Seek professional advice if you notice any changes."
        )

    st.divider()
    
    # ======================
    # Map Section (show only after analysis)
    # ======================
    if "city" not in st.session_state:
        st.session_state.city = ""

    st.subheader("📍 Find Nearby Dermatologists")

    city = st.text_input(
        "Enter your city or area",
        value=st.session_state.city
    )

    if st.button("Search Dermatologists"):
        st.session_state.city = city

    if st.session_state.city:
        maps_url = f"https://www.google.com/maps/search/dermatologist+near+{st.session_state.city.replace(' ', '+')}"
        st.markdown(f"**[View Nearby Dermatologists on Map]({maps_url})**")
        st.info("🔗 Click the link above to open Google Maps in a new tab.")