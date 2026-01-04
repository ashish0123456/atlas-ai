from pathlib import Path
from pypdf import PdfReader
from app.observability.logger import JsonLogger

logger = JsonLogger("document-loader")


def load_document(file_path: Path) -> str:
    """
    Load text content from a document file.
    
    Supported formats:
    - PDF (.pdf)
    - Text files (.txt)
    - Markdown (.md)
    
    Args:
        file_path: Path to the document file
    
    Returns:
        Extracted text content
    
    Raises:
        ValueError: If file format is not supported or file cannot be read
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    file_ext = file_path.suffix.lower()
    
    try:
        if file_ext == '.pdf':
            try:
                reader = PdfReader(str(file_path))
                if len(reader.pages) == 0:
                    raise ValueError(f"PDF file has no pages: {file_path}")
                
                text = ""
                for i, page in enumerate(reader.pages):
                    try:
                        page_text = page.extract_text() or ""
                        text += page_text + "\n"
                    except Exception as e:
                        logger.log(
                            "WARN",
                            "page_extraction_failed",
                            file_path=str(file_path),
                            page=i,
                            error=str(e)
                        )
                
                if not text.strip():
                    raise ValueError(f"PDF file contains no extractable text: {file_path}")
                
                return text.strip()
            except Exception as pdf_error:
                logger.log(
                    "ERROR",
                    "pdf_loading_failed",
                    file_path=str(file_path),
                    error=str(pdf_error),
                    error_type=type(pdf_error).__name__
                )
                raise
        
        elif file_ext in ['.txt', '.md']:
            return file_path.read_text(encoding="utf-8")
        
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    
    except Exception as e:
        logger.log(
            "ERROR",
            "document_load_failed",
            file_path=str(file_path),
            error=str(e)
        )
        raise