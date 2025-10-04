import os
import time
import streamlit as st
from google import genai
from google.genai import types

# Title
st.title("🐶 Gemini Video Generator")
st.write("Generate short videos using Google Gemini AI.")

# Load API Key
API_KEY = os.getenv("AIzaSyD6c-tdr0Da6-4gwa2o8WSA9Ftn6TDPOx0")

if not API_KEY:
    st.error(
        """
        ❌ GEMINI_API_KEY not found.
        
        **How to fix:**
        1. Locally: create a `.env` file with `GEMINI_API_KEY=your_api_key_here`.
        2. Deployment: add the key as a secret/environment variable on your platform:
           - Streamlit Cloud: Settings → Secrets
           - Render/Heroku/etc.: Environment Variables
        """
    )
    st.stop()  # Stop app if no key

# Init Gemini client
try:
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error(f"❌ Failed to initialize Gemini client: {e}")
    st.stop()

# User inputs
prompt = st.text_input(
    "Video prompt", 
    "A close-up shot of a golden retriever playing in a field of sunflowers"
)
negative_prompt = st.text_input("Negative prompt (things to avoid)", "barking, woofing")
aspect_ratio = st.selectbox("Aspect ratio", ["16:9", "9:16", "1:1"], index=1)
resolution = st.selectbox("Resolution", ["480p", "720p", "1080p"], index=1)

# Generate video
if st.button("Generate Video"):
    with st.spinner("⏳ Generating video... this may take a few minutes"):
        try:
            operation = client.models.generate_videos(
                model="veo-3.0-fast-generate-001",
                prompt=prompt,
                config=types.GenerateVideosConfig(
                    negative_prompt=negative_prompt,
                    aspect_ratio=aspect_ratio,
                    resolution=resolution,
                ),
            )

            # Poll until operation is done
            progress_bar = st.progress(0)
            while not operation.done:
                time.sleep(20)
                operation = client.operations.get(operation.name)
                progress_bar.progress(min(progress_bar.progress + 10, 100))
                st.info("Still generating...")

            # Get result
            generated_video = operation.response.generated_videos[0]
            downloaded = client.files.download(file=generated_video.video)

            # Save to local file
            output_file = "generated_video.mp4"
            with open(output_file, "wb") as f:
                f.write(downloaded.read())

            st.success(f"✅ Video saved as {output_file}")
            st.video(output_file)

        except Exception as e:
            st.error(f"❌ Error generating video: {e}")
            st.stop()
