import re
import os

with open('data/raw_pdf.txt', 'r', encoding='utf-8') as f:
    pdf_text = f.read()

# Clean OCR artifacts
pdf_text = pdf_text.replace('\\n', '\n')
pdf_text = pdf_text.replace('\\"', '"')
pdf_text = re.sub(r'==Screenshot for page \d+==', '', pdf_text)
pdf_text = re.sub(r'==Start of OCR for page \d+==', '', pdf_text)
pdf_text = re.sub(r'==End of OCR for page \d+==', '', pdf_text)
pdf_text = pdf_text.replace('==Start of PDF==', '')
pdf_text = pdf_text.replace('==End of PDF==', '')

# Split by Program titles
split_pattern = r'\n(?=(?:Bachelor of|Doctor of|Plan \d+ |Thai Major|History Major|Philosophy Major|Chinese Major|Japanese Language|Korean Language|German Language|Indian Languages|Faculty of)\b)'
chunks = re.split(split_pattern, pdf_text)

os.makedirs('data/conditions', exist_ok=True)
count = 0

for chunk in chunks:
    chunk = chunk.strip()
    if not chunk: continue
    
    lines = [l.strip() for l in chunk.split('\n') if l.strip()]
    if not lines: continue
    
    title_line = lines[0]
    filename = re.sub(r'[\\/*?:"<>|]', '', title_line)
    filename = filename.replace('\n', ' ').strip()
    if len(filename) > 100: filename = filename[:100].strip()
        
    filepath = f"data/conditions/{filename}.md"
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("# " + chunk)
        print(f"Saved: {filepath}")
        count += 1

print(f"\nSuccessfully extracted {count} files!")
