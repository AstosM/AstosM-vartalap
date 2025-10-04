import os
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

def init_client():
    load_dotenv()
    api_key = os.getenv("AIzaSyCxYlgND-IyD4CtRNDFouGreb4xBeaI9gA")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set in environment or .env")
    client = genai.Client(api_key=api_key)
    return client

def generate_video(prompt: str, model: str = "veo-3.0-generate-preview", negative_prompt: str = None) -> str:
    """
    Calls Gemini API to generate a video from prompt.
    Returns a URL or path to the generated video (or writes to local file).
    """
    client = init_client()

    # Create config if needed
    config = types.GenerateVideosConfig()
    if negative_prompt:
        config.negative_prompt = negative_prompt

    # Kick off long-running video generation operation
    operation = client.models.generate_videos(
        model=model,
        prompt=prompt,
        config=config,
    )

    # The operation may not complete immediately — poll until done
    # Depending on SDK, you may have operation.result() or operations API
    result = operation.result()  # block until done (or timeout)
    # result might contain video URI(s), etc.
    # Let's assume result returns something like result.video_uris or result.outputs

    # For demonstration, we assume one video and we can download it
    if hasattr(result, "outputs") and result.outputs:
        output = result.outputs[0]
        uri = output.uri  # e.g. a GCS URI or HTTPS URL
        # Optionally download it locally
        local_path = download_from_uri(uri)
        return local_path
    else:
        raise RuntimeError(f"No video output in result: {result}")

def download_from_uri(uri: str) -> str:
    """
    Download a video from a URI to a local file.
    Supports https or GCS (if authenticated).
    """
    import requests
    # simple https download
    resp = requests.get(uri, stream=True)
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to download video from {uri}, status {resp.status_code}")
    fname = uri.split("/")[-1]
    with open(fname, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return fname

if __name__ == "__main__":
    prompt = "A calm lake at dawn, sunlight glinting on the water, mist rising slowly, soft ambient birdsong"
    output_path = generate_video(prompt)
    print("Saved video to:", output_path)
