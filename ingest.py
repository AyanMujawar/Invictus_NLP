import pdfplumber

def extract_text(pdf_path: str) -> str:
    parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            parts.append(page.extract_text() or "")
    return "\n".join(parts)

def chunk_text(text: str, words_per_chunk: int = 800, overlap: int = 100):
    words = text.split()
    chunks, i = [], 0
    while i < len(words):
        chunks.append(" ".join(words[i:i + words_per_chunk]))
        i += words_per_chunk - overlap
    return chunks