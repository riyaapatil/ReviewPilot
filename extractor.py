# extractor.py
import pymupdf as fitz
from pydantic import BaseModel
from typing import Optional

class PaperInfo(BaseModel):
    title: str
    authors: str
    # Added Optional and = None to prevent crashes if the LLM can't find them
    publication_year: Optional[str] = None
    publication_venue: Optional[str] = None
    technologies_used: Optional[str] = None
    objective: str
    methodology: str
    dataset: Optional[str] = None
    key_findings: str
    advantages: Optional[str] = None
    limitations: Optional[str] = None

def extract_text_from_pdf(pdf_path: str, max_chars: int = 12000) -> str:
    """Extract PDF text with page markers."""
    doc = fitz.open(pdf_path)
    full_text = ""
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text()
        full_text += f"\n--- Page {page_num} ---\n{text}"
    doc.close()
    
    return full_text[:max_chars]