import os
import pdfplumber
from pathlib import Path
from tqdm import tqdm

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        print(f"\n[Error] Failed to read {pdf_path.name}: {e}")
    return text

def main():
    base_dir = Path(__file__).parent.parent
    pdf_dir = base_dir / 'data' / 'pdf'
    output_dir = base_dir / 'data' / 'raw_text'

    if not pdf_dir.exists():
        print(f"Directory not found: {pdf_dir}")
        return

    # Find all PDFs
    pdf_files = list(pdf_dir.rglob("*.pdf"))
    if not pdf_files:
        print("No PDF files found.")
        return

    print(f"Found {len(pdf_files)} PDF files to process.")
    
    # Process with progress bar
    for pdf_path in tqdm(pdf_files, desc="Extracting PDFs", unit="file"):
        # Determine the relative path to maintain folder structure (e.g. Faculty Name)
        rel_path = pdf_path.relative_to(pdf_dir)
        
        # Create corresponding output directory
        out_file_dir = output_dir / rel_path.parent
        out_file_dir.mkdir(parents=True, exist_ok=True)
        
        out_file_path = out_file_dir / f"{pdf_path.stem}.txt"
        
        # Skip if already extracted
        if out_file_path.exists():
            continue
            
        text = extract_text_from_pdf(pdf_path)
        
        if text.strip():
            with open(out_file_path, "w", encoding="utf-8") as f:
                f.write(text)

    print("\nExtraction completed! Check the 'data/raw_text' folder.")

if __name__ == "__main__":
    main()
