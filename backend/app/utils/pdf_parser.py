import fitz  # PyMuPDF
import re
from typing import List

def extract_clean_text_from_pdf(pdf_path: str) -> str:
    """
    Opens a PDF file, extracts the raw text from all pages, 
    and cleans up common PDF artifact formatting messes.
    """
    doc = fitz.open(pdf_path)
    full_text = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        
        # Basic cleanup per page to help the LLM context boundary
        text = clean_page_text(text)
        full_text.append(text)
        
    doc.close()
    return "\n\n--- PAGE BREAK ---\n\n".join(full_text)

def clean_page_text(text: str) -> str:
    """
    Removes erratic whitespaces, fixes broken words caused by line-wraps,
    and formats page headers/footers cleanly.
    """
    # Remove multiple consecutive whitespaces, keeping single spaces
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Fix hyphenated split-words across line breaks (e.g., "agree-\nment" -> "agreement")
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
    
    # Standardize erratic line breaks to keep clauses readable
    text = re.sub(r'\n+', '\n', text)
    
    return text.strip()

def chunk_text_by_size(text: str, max_chars: int = 4000) -> List[str]:
    """
    Splits massive legal text into manageable blocks so we don't
    hit token context limit ceilings with the Groq API.
    """
    paragraphs = text.split("\n")
    chunks = []
    current_chunk = []
    current_length = 0
    
    for paragraph in paragraphs:
        # If adding this paragraph exceeds limits, flush the current chunk
        if current_length + len(paragraph) > max_chars and current_chunk:
            chunks.append("\n".join(current_chunk))
            current_chunk = []
            current_length = 0
            
        current_chunk.append(paragraph)
        current_length += len(paragraph) + 1
        
    if current_chunk:
        chunks.append("\n".join(current_chunk))
        
    return chunks