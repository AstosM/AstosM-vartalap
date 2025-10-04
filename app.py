import os
import requests
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load .env
load_dotenv()
API_KEY = os.getenv("AIzaSyD6c-tdr0Da6-4gwa2o8WSA9Ftn6TDPOx0")
if not API_KEY:
    st.error("⚠️ GEMINI_API_KEY not found. Add it to .env or export as env var.")
    st.stop()

# Init Gemini client
client = genai.Client(api_key=API_KEY)

# Streamlit config
st.set_page_config(page_title="🎬 Gemini Video Generator", layout="centered")
st.title("🎬 Gemini Veo Video Generator")

# Input box
prompt = st.text_area("Enter your video prompt:", placeholder="e.g., A futuristic city with flying cars at sunset")

model_choice = st.selectbox(
    "Choose model",
    ["veo-3.0-generate-preview", "veo-3.0-fast-generate-preview"]
)

def download_video(uri: str, filename: str = "generated_video.mp4") -> str:
    """Download video file locally from URI"""
    resp = requests.get(uri, stream=True)
    if resp.status_code != 200:
        raise RuntimeError(f"Download failed: {resp.status_code} {resp.text}")
    with open(filename, "wb") as f:
        for chunk in resp.iter_content(8192):
            f.write(chunk)
    return filename

# Generate button
if st.button("Generate Video 🎥"):
    if not prompt.strip():
        st.warning("Please enter a prompt first!")
    else:
        with st.spinner("⏳ Generating video... this may take a few minutes"):
            try:
                config = types.GenerateVideosConfig()
                operation = client.models.generate_videos(
                    model=model_choice,
                    prompt=prompt,
                    config=config,
                )
                result = operation.result()  # wait until ready

                if not result.outputs:
                    st.error("No video generated. Try again with a different prompt.")
                else:
                    video_uri = result.outputs[0].uri
                    local_file = download_video(video_uri, "generated_video.mp4")
                    st.success("✅ Video generated successfully!")
                    st.video(local_file)
                    st.download_button(
                        "⬇️ Download Video",
                        data=open(local_file, "rb").read(),
                        file_name="gemini_video.mp4",
                        mime="video/mp4"
                    )

            except Exception as e:
                st.error(f"Error: {e}")
