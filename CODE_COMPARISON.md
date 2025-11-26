# Code Comparison: Before vs After

## 1. Main Application Entry Point

### ❌ Before (main.py)
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import List
from fastapi import File, UploadFile
from fastapi import HTTPException
from services import load_documents
from agents import classify_documents, extract_documents
import traceback

# Logging configured inline
logging.basicConfig(level=logging.INFO,format='...')
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    yield
    logger.info("Shutting down...")

# Hardcoded values
app = FastAPI(
    title = "SUPERCLAIMS API",
    lifespan=lifespan
)

# Everything in one file
@app.post("/generate-claim")
async def generate_claim(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    try:
        if not files:  # Duplicate check
            raise HTTPException(status_code=400, detail="Failed to load any documents")

        loaded_documents = await load_documents(files)
        classification_results = classify_documents(loaded_documents)
        extraction_results = await extract_documents(classification_results, loaded_documents)

        return {
            "classification": classification_results.model_dump(),
            "extraction": extraction_results.model_dump()
        }
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error processing files: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing files: {str(e)}")
```

### ✅ After (app/main.py)
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.exceptions import setup_exception_handlers
from app.api.v1 import api_router

# Centralized configuration
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup")
    yield
    logger.info("Application shutdown")

# Configuration from settings
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Centralized exception handling
setup_exception_handlers(app)

# Versioned API with router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
```

**Improvements:**
- ✅ Separated concerns (endpoint logic moved to routers)
- ✅ Centralized configuration
- ✅ Custom exception handlers
- ✅ API versioning
- ✅ No duplicate checks
- ✅ Cleaner, more maintainable

---

## 2. Configuration Management

### ❌ Before (Scattered)
```python
# In services/ai_models.py
from dotenv import load_dotenv
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=GOOGLE_API_KEY)

# In services/document_loader.py
DOCUMENTS_DIR = Path("uploaded_documents")

# In main.py
app = FastAPI(title = "SUPERCLAIMS API")
```

### ✅ After (app/config.py)
```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)
    
    APP_NAME: str = "SUPERCLAIMS API"
    API_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    GOOGLE_API_KEY: str
    LLM_MODEL: str = "gemini-2.5-flash"
    LLM_TEMPERATURE: float = 0.0
    LLM_MAX_RETRIES: int = 3
    
    ALLOWED_ORIGINS: List[str] = ["*"]
    LOG_LEVEL: str = "INFO"
    
    UPLOAD_DIR: str = "uploaded_documents"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024
    ALLOWED_FILE_TYPES: List[str] = [".pdf"]

settings = Settings()
```

**Improvements:**
- ✅ Single source of truth
- ✅ Type-safe access
- ✅ Environment-specific settings
- ✅ Validation with Pydantic
- ✅ Default values clearly defined

---

## 3. LLM Initialization

### ❌ Before (services/ai_models.py)
```python
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv()
import os

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Created fresh every import
model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=GOOGLE_API_KEY
)
```

### ✅ After (app/core/llm.py)
```python
from functools import lru_cache
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import settings

@lru_cache(maxsize=1)
def get_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=settings.LLM_MODEL,
        api_key=settings.GOOGLE_API_KEY,
        temperature=settings.LLM_TEMPERATURE,
        max_retries=settings.LLM_MAX_RETRIES,
    )
```

**Improvements:**
- ✅ Cached (created only once)
- ✅ Configuration from settings
- ✅ Function-based (easier to test)
- ✅ More configurable

---

## 4. Document Classification

### ❌ Before (agents/document_agent.py)
```python
from dotenv import load_dotenv
import os
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Models defined in agent file
class DocumentType(str, Enum):
    BILL = "BILL"
    # ...

class ClassificationResult(BaseModel):
    # ...

from services import model  # Direct import

structured_model = model.with_structured_output(ClassificationResult)

def classify_documents(all_documents) -> ClassificationResult:
    documents_text = "\n\n".join([...])
    prompt = f"""Analyze and classify..."""  # Hardcoded prompt
    
    result = structured_model.invoke(prompt)  # Synchronous
    return result
```

### ✅ After (app/agents/classification.py)
```python
from langchain_core.documents import Document
from typing import List
import asyncio
import logging

from app.schemas.classification import ClassificationResult
from app.core.prompts import CLASSIFICATION_PROMPT
from app.core.llm import get_llm
from app.exceptions import ClassificationError

logger = logging.getLogger(__name__)

class DocumentClassifier:
    def __init__(self):
        self.llm = get_llm()
        self.structured_llm = self.llm.with_structured_output(ClassificationResult)
    
    async def classify(self, documents: List[Document]) -> ClassificationResult:
        try:
            logger.info(f"Starting classification for {len(documents)} document pages")
            
            documents_text = "\n\n".join([
                f"Source: {doc.metadata.get('source', 'Unknown')}, Page: {doc.metadata.get('page', 'Unknown')}\n{doc.page_content}"
                for doc in documents
            ])
            
            prompt = CLASSIFICATION_PROMPT.format(documents_text=documents_text)
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.structured_llm.invoke,
                prompt
            )
            
            logger.info("Classification completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Classification failed: {str(e)}")
            raise ClassificationError(detail=f"Failed to classify documents: {str(e)}")
```

**Improvements:**
- ✅ Class-based (better encapsulation)
- ✅ Async support
- ✅ Prompts in separate file
- ✅ Models in schemas
- ✅ Custom exception handling
- ✅ Better logging
- ✅ Type hints

---

## 5. Document Loading

### ❌ Before (services/document_loader.py)
```python
from langchain_community.document_loaders import PyPDFLoader, UnstructuredImageLoader, TextLoader
from langchain_core.documents import Document
from pathlib import Path
from fastapi import UploadFile
from typing import List
import os
import re

DOCUMENTS_DIR = Path("uploaded_documents")  # Hardcoded

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
    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
    doc_number = get_next_document_number()

    for file in files:  # Sequential processing
        file_extension = Path(file.filename).suffix
        stored_filename = f"doc_{doc_number}{file_extension}"
        stored_file_path = DOCUMENTS_DIR / stored_filename
        
        content = await file.read()
        with open(stored_file_path, 'wb') as f:  # Not async
            f.write(content)
        
        document = load_document(str(stored_file_path))
        
        for page_num, doc in enumerate(document, start=1):
            doc.metadata["source"] = stored_filename
            doc.metadata["page"] = page_num
        
        results.extend(document)
        doc_number += 1

    return results
```

### ✅ After (app/services/document_loader.py)
```python
from pathlib import Path
from typing import List
import asyncio
import re
from fastapi import UploadFile, HTTPException, status
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
import logging

from app.config import settings
from app.exceptions import DocumentProcessingError

logger = logging.getLogger(__name__)

class DocumentLoaderService:
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        self.loaders = {
            '.pdf': PyPDFLoader,
        }
    
    def validate_file(self, file: UploadFile) -> None:
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is required"
            )
        
        extension = Path(file.filename).suffix.lower()
        
        if extension not in settings.ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {extension} not supported"
            )
        
        if hasattr(file, 'size') and file.size and file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum"
            )
    
    async def save_file(self, file: UploadFile, doc_number: int) -> Path:
        extension = Path(file.filename).suffix
        filename = f"doc_{doc_number}{extension}"
        filepath = self.upload_dir / filename
        
        try:
            content = await file.read()
            with open(filepath, 'wb') as f:
                f.write(content)
            logger.info(f"Saved file: {filename}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving file {filename}: {str(e)}")
            raise DocumentProcessingError(
                detail=f"Failed to save file: {str(e)}",
                filename=file.filename
            )
    
    def load_single_document(self, filepath: Path) -> List[Document]:
        extension = filepath.suffix.lower()
        loader_class = self.loaders.get(extension)
        
        if not loader_class:
            raise ValueError(f"No loader available for {extension}")
        
        try:
            loader = loader_class(str(filepath))
            return loader.load()
        except Exception as e:
            logger.error(f"Error loading document {filepath.name}: {str(e)}")
            raise DocumentProcessingError(
                detail=f"Failed to load document: {str(e)}",
                filename=filepath.name
            )
    
    async def load_documents(self, files: List[UploadFile]) -> List[Document]:
        # Validate all files first
        for file in files:
            self.validate_file(file)
        
        doc_number = self._get_next_doc_number()
        results = []
        
        # Concurrent file saving
        save_tasks = [
            self.save_file(file, doc_number + i) 
            for i, file in enumerate(files)
        ]
        saved_paths = await asyncio.gather(*save_tasks)
        
        # Concurrent document loading
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
        
        logger.info(f"Successfully loaded {len(results)} pages from {len(files)} files")
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
```

**Improvements:**
- ✅ Class-based service
- ✅ File validation (size, type, name)
- ✅ Concurrent file operations
- ✅ Better error handling
- ✅ Custom exceptions
- ✅ Configuration from settings
- ✅ Comprehensive logging

---

## 6. API Endpoint

### ❌ Before (in main.py)
```python
@app.post("/generate-claim")
async def generate_claim(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    try:
        if not files:  # Duplicate
            raise HTTPException(status_code=400, detail="Failed to load any documents")

        loaded_documents = await load_documents(files)
        logger.info(f"Successfully loaded {len(loaded_documents)} documents")

        classification_results = classify_documents(loaded_documents)
        logger.info(f"Classification complete")

        extraction_results = await extract_documents(classification_results, loaded_documents)
        logger.info(f"Extraction complete")

        return {
            "classification": classification_results.model_dump(),
            "extraction": extraction_results.model_dump()
        }
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error processing files: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing files: {str(e)}")
```

### ✅ After (app/api/v1/endpoints/claims.py)
```python
from typing import List
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from pydantic import BaseModel
import logging

from app.api.deps import DocumentLoaderDep, ClassifierDep, ExtractorDep
from app.schemas.classification import ClassificationResult
from app.schemas.extraction import ExtractionResponse

router = APIRouter()
logger = logging.getLogger(__name__)

class ClaimGenerationResponse(BaseModel):
    classification: ClassificationResult
    extraction: ExtractionResponse

@router.post(
    "/generate-claim",
    response_model=ClaimGenerationResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate insurance claim from documents",
    response_description="Classified and extracted document data"
)
async def generate_claim(
    files: List[UploadFile] = File(..., description="Documents for claim generation"),
    loader: DocumentLoaderDep = None,
    classifier: ClassifierDep = None,
    extractor: ExtractorDep = None
) -> ClaimGenerationResponse:
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided"
        )
    
    logger.info(f"Processing {len(files)} files for claim generation")
    
    documents = await loader.load_documents(files)
    logger.info(f"Successfully loaded {len(documents)} document pages")
    
    classification = await classifier.classify(documents)
    logger.info("Classification complete")
    
    extraction = await extractor.extract_batch(classification, documents)
    logger.info(f"Extraction complete: {extraction.successful_extractions}/{extraction.total_extracted}")
    
    return ClaimGenerationResponse(
        classification=classification,
        extraction=extraction
    )
```

**Improvements:**
- ✅ Separate router module
- ✅ Dependency injection
- ✅ Response model defined
- ✅ Proper status codes
- ✅ OpenAPI documentation
- ✅ No duplicate checks
- ✅ Better error handling via custom exceptions
- ✅ Type-safe return

---

## Summary of Key Improvements

| Aspect | Before | After |
|--------|--------|-------|
| **Structure** | Flat, mixed concerns | Layered, separated concerns |
| **Configuration** | Scattered, hardcoded | Centralized, type-safe |
| **Performance** | Sequential processing | Concurrent operations |
| **Error Handling** | Generic exceptions | Custom exceptions with handlers |
| **Testing** | Hard to test | Easy with dependency injection |
| **Maintainability** | Coupled code | Loose coupling |
| **Documentation** | Minimal | Auto-generated + comprehensive |
| **Type Safety** | Partial | Complete type hints |
| **Scalability** | Limited | Highly scalable |

**Total lines of organized code:** ~22 files with clear separation of concerns
**Eliminated:** Duplicate models, scattered config, mixed responsibilities
**Added:** Error handling, validation, concurrency, caching, proper architecture

