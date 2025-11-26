from pathlib import Path
from typing import List
import asyncio
import re
from fastapi import UploadFile, HTTPException
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader

from app.config import settings

class DocumentLoaderService:
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        self.loaders = {
            '.pdf': PyPDFLoader,
        }
    
    def validate_file(self, file: UploadFile) -> None:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")
        
        extension = Path(file.filename).suffix.lower()
        
        if extension != '.pdf':
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
    
    async def save_file(self, file: UploadFile, doc_number: int) -> Path:
        extension = Path(file.filename).suffix
        filename = f"doc_{doc_number}{extension}"
        filepath = self.upload_dir / filename
        
        content = await file.read()
        with open(filepath, 'wb') as f:
            f.write(content)
        return filepath
    
    def load_single_document(self, filepath: Path) -> List[Document]:
        extension = filepath.suffix.lower()
        loader_class = self.loaders.get(extension)
        
        if not loader_class:
            raise ValueError(f"No loader available for {extension}")
        
        loader = loader_class(str(filepath))
        return loader.load()
    
    async def load_documents(self, files: List[UploadFile]) -> List[Document]:
        for file in files:
            self.validate_file(file)
        
        doc_number = self._get_next_doc_number()
        results = []
        
        save_tasks = [
            self.save_file(file, doc_number + i) 
            for i, file in enumerate(files)
        ]
        saved_paths = await asyncio.gather(*save_tasks)
        
        loop = asyncio.get_event_loop()
        load_tasks = [
            loop.run_in_executor(None, self.load_single_document, path)
            for path in saved_paths
        ]
        documents_lists = await asyncio.gather(*load_tasks)
        
        for filepath, docs in zip(saved_paths, documents_lists):
            for page_num, doc in enumerate(docs, 1):
                doc.metadata["source"] = filepath.name
                doc.metadata["page"] = page_num
            results.extend(docs)
        
        return results
    
    def _get_next_doc_number(self) -> int:
        existing = list(self.upload_dir.glob("doc_*"))
        if not existing:
            return 1
        
        numbers = []
        for file in existing:
            match = re.match(r'doc_(\d+)', file.stem)
            if match:
                numbers.append(int(match.group(1)))
        
        return max(numbers, default=0) + 1

