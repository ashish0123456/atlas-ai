from pathlib import Path
from pypdf import PdfReader


def load_document(file_path: Path) -> str:
    if file_path.suffix.lower() == '.pdf':
        reader = PdfReader(str(file_path))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    
    # fallback to .txt files
    return file_path.read_text(encoding="utf-8")