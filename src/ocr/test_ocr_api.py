import requests
import pypdfium2 as pdfium
import io
import os

pdf_path = "Minor_extracted/Minor/คณะวิทยาศาสตร์.pdf"

# Convert first page to image
pdf = pdfium.PdfDocument(pdf_path)
page = pdf[0]
bitmap = page.render(scale=2)
pil_image = bitmap.to_pil()

# Save to bytes
img_byte_arr = io.BytesIO()
pil_image.save(img_byte_arr, format='PNG')
img_byte_arr = img_byte_arr.getvalue()

# Send to OCR.space API
url = "https://api.ocr.space/parse/image"
payload = {
    'apikey': 'helloworld',
    'language': 'tha',
    'isOverlayRequired': False
}
files = {'file': ('image.png', img_byte_arr, 'image/png')}

print("Sending request to OCR.space...")
response = requests.post(url, data=payload, files=files)
try:
    result = response.json()
    if 'ParsedResults' in result:
        text = result['ParsedResults'][0]['ParsedText']
        print("--- EXTRACTED TEXT ---")
        print(text)
    else:
        print("API Response:")
        print(result)
except Exception as e:
    print(f"Error: {e}")
    print(response.text)
