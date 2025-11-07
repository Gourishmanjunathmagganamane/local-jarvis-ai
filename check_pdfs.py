# save as check_pdfs.py
import os
from PyPDF2 import PdfReader

data_path = "data"

for file in os.listdir(data_path):
    if file.endswith(".pdf"):
        try:
            path = os.path.join(data_path, file)
            reader = PdfReader(path)
            _ = len(reader.pages)
            print(f"✅ {file} - OK ({len(reader.pages)} pages)")
        except Exception as e:
            print(f"❌ {file} - Corrupted or invalid PDF: {e}")
