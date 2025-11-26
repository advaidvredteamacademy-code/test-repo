from langchain_community.document_loaders import PyPDFLoader, UnstructuredImageLoader, TextLoader
from langchain_core.documents import Document
from pathlib import Path
from fastapi import UploadFile
from typing import List
import os
import re

# Directory to store uploaded documents
DOCUMENTS_DIR = Path("uploaded_documents")

def get_next_document_number() -> int:
    """Get the next available document number based on existing files."""
    if not DOCUMENTS_DIR.exists():
        DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
        return 1
    
    # Find all files matching doc_N pattern
    existing_files = list(DOCUMENTS_DIR.glob("doc_*"))
    if not existing_files:
        return 1
    
    # Extract numbers from filenames
    numbers = []
    for file in existing_files:
        # Match doc_NUMBER (with or without extension)
        match = re.match(r'doc_(\d+)', file.stem)
        if match:
            numbers.append(int(match.group(1)))
    
    return max(numbers) + 1 if numbers else 1


def load_document(file_path: str) -> Document:
    path = Path(file_path)
    extension = path.suffix.lower()
    
    if extension == '.pdf':
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        return pages

    
    else:
        raise ValueError(f"Unsupported file type: {extension}")


async def load_documents(files: List[UploadFile]) -> list[Document]:
    results = []
    
    # Ensure the documents directory exists
    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Get starting document number
    doc_number = get_next_document_number()

    for file in files:
        file_extension = Path(file.filename).suffix
        
        # Create sequential filename: doc_1.pdf, doc_2.pdf, etc.
        stored_filename = f"doc_{doc_number}{file_extension}"
        stored_file_path = DOCUMENTS_DIR / stored_filename
        
        # Write file to persistent storage
        content = await file.read()
        with open(stored_file_path, 'wb') as f:
            f.write(content)
        
        # Load the document
        document = load_document(str(stored_file_path))
        
        # Add metadata with page numbers
        for page_num, doc in enumerate(document, start=1):
            doc.metadata["source"] = stored_filename
            doc.metadata["page"] = page_num
        
        results.extend(document)
        doc_number += 1

    return results
