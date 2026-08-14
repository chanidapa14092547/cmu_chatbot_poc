import pytesseract
from PIL import Image
import sys

files = [
    "/Users/memee/.gemini/antigravity/brain/2841b509-7aa0-400e-b3b2-e234614fe2ae/.user_uploaded/media__1785914703815.png",
    "/Users/memee/.gemini/antigravity/brain/2841b509-7aa0-400e-b3b2-e234614fe2ae/.user_uploaded/media__1785914703817.png"
]

for file in files:
    try:
        print(f"--- OCR for {file} ---")
        img = Image.open(file)
        # Using Thai language if installed, otherwise eng
        text = pytesseract.image_to_string(img, lang='tha+eng')
        print(text)
    except Exception as e:
        print(f"Error processing {file}: {e}")

