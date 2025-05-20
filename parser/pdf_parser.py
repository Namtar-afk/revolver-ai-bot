import pdfplumber
from pathlib import Path
from typing import Optional

def extract_text_from_pdf(file_path: str) -> Optional[str]:
    try:
        with pdfplumber.open(Path(file_path)) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    except Exception as e:
        print(f"[ERROR] Failed to extract PDF text: {e}")
        return None
