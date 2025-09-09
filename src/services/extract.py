"""Text extraction services for resume files."""

import os
import pypdf
import docx2txt
from typing import Optional

def extract_text_from_pdf(file_path: str) -> Optional[str]:
    """Extract text from a PDF file."""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
    except Exception as e:
        print(f"Error extracting text from PDF {file_path}: {e}")
        return None

def extract_text_from_docx(file_path: str) -> Optional[str]:
    """Extract text from a DOCX file."""
    try:
        text = docx2txt.process(file_path)
        return text.strip() if text else None
    except Exception as e:
        print(f"Error extracting text from DOCX {file_path}: {e}")
        return None

def extract_text_from_doc(file_path: str) -> Optional[str]:
    """Extract text from a DOC file (legacy format)."""
    # For DOC files, we'll try to use docx2txt which sometimes works
    # In a production environment, you might want to use python-docx2txt or antiword
    try:
        text = docx2txt.process(file_path)
        return text.strip() if text else None
    except Exception as e:
        print(f"Error extracting text from DOC {file_path}: {e}")
        return None

def extract_text_from_file(file_path: str) -> Optional[str]:
    """Extract text from a file based on its extension."""
    if not os.path.exists(file_path):
        return None
    
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_extension == '.docx':
        return extract_text_from_docx(file_path)
    elif file_extension == '.doc':
        return extract_text_from_doc(file_path)
    else:
        print(f"Unsupported file type: {file_extension}")
        return None
