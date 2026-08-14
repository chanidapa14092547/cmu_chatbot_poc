# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "google-genai",
#     "pillow",
# ]
# ///

import os
from google import genai
from PIL import Image

# Initialize the client. We assume GEMINI_API_KEY is in the environment
# But if it is not, we'll try to extract it from the agent's known config or just ask the user for it if it fails.
# Let's hope the environment has GEMINI_API_KEY.

try:
    client = genai.Client()
except Exception as e:
    print(f"Error initializing client: {e}")
    print("Please set GEMINI_API_KEY environment variable.")
    exit(1)

files = [
    "/Users/memee/.gemini/antigravity/brain/2841b509-7aa0-400e-b3b2-e234614fe2ae/.user_uploaded/media__1785914703815.png",
    "/Users/memee/.gemini/antigravity/brain/2841b509-7aa0-400e-b3b2-e234614fe2ae/.user_uploaded/media__1785914703817.png"
]

for file in files:
    print(f"--- OCR for {file} ---")
    img = Image.open(file)
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[img, "Extract all the text in this image, especially the rules and conditions. Keep the original Thai wording exact."]
    )
    print(response.text)
