import os
import time
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("❌ GEMINI_API_KEY not set. Add it to .env or export as environment variable.")
    st.stop()

# Init Gemini client
client = genai.Client(api_key=API_KEY)

st.title("🐶 Gemini Video Generator")
st.write("Generate a short video using Google Gemini AI.")

# User inputs
prompt = st.text_input("Video prompt", "A close-up shot of a golden retriever playing in a field of sunflowers")
negative_prompt = st.text_input("Negative prompt (things to avoid)", "barking, woofing")
aspect_ratio = st.selectbox("Aspect ratio", ["16:9", "9:16", "1:1"], index=1)
resolution = st.selectbox("Resolution", ["480p", "720p", "1080p"], index=1)

if st.button("Generate Video"):
    with st.spinner("⏳ Generating video... this may take a few minutes"):
        try:
            # Start video generation
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
            while not operation.done:
                time.sleep(20)
                operation = client.operations.get(operation.name)
                st.info("Still generating...")

            # Get result
            generated_video = operation.response.generated_videos[0]
            downloaded = client.files.download(file=generated_video.video)

            # Save to a local file
            output_file = "generated_video.mp4"
            with open(output_file, "wb") as f:
                f.write(downloaded.read())

            st.success(f"✅ Video saved as {output_file}")
            st.video(output_file)  # Display in Streamlit
        except Exception as e:
            st.error(f"❌ Error generating video: {e}")
