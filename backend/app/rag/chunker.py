from typing import List


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100):
    """
    Split and yield text into overlapping chunks.
    
    Args:
        text: Text to chunk
        chunk_size: Size of each chunk in characters
        overlap: Number of characters to overlap between chunks
    
    """
    if not text or not text.strip():
        return []
    
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be non-negative and less than chunk_size")
    
    text_length = len(text)
    step = chunk_size - overlap
    start = 0

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end].strip()

        if chunk:
            yield chunk

        start += step
