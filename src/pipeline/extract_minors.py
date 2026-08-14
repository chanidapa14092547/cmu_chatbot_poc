import os
import pdfplumber

minor_dir = "Minor_extracted/Minor"
output_file = "minor_extracted_text.txt"

with open(output_file, 'w', encoding='utf-8') as out_f:
    for filename in os.listdir(minor_dir):
        if filename.endswith(".pdf"):
            filepath = os.path.join(minor_dir, filename)
            out_f.write(f"--- File: {filename} ---\n")
            try:
                with pdfplumber.open(filepath) as pdf:
                    for i, page in enumerate(pdf.pages):
                        text = page.extract_text()
                        if text:
                            out_f.write(text + "\n")
            except Exception as e:
                out_f.write(f"Error reading {filename}: {e}\n")
            out_f.write("\n===================================\n\n")

print(f"Extraction complete. Saved to {output_file}")
