from typing import List
from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel

from app.services.document_loader import DocumentLoaderService
from app.agents.classification import DocumentClassifier
from app.agents.extraction import DocumentExtractor
from app.schemas.classification import ClassificationResult
from app.schemas.extraction import ExtractionResponse

router = APIRouter()

class ClaimGenerationResponse(BaseModel):
    classification: ClassificationResult
    extraction: ExtractionResponse

@router.post("/generate-claim", response_model=ClaimGenerationResponse)
async def generate_claim(
    files: List[UploadFile] = File(...)
) -> ClaimGenerationResponse:
    """Generate insurance claim from uploaded documents"""
    
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    try:
        # Instantiate services directly
        loader = DocumentLoaderService()
        classifier = DocumentClassifier()
        extractor = DocumentExtractor()
        
        documents = await loader.load_documents(files)
        classification = await classifier.classify(documents)
        extraction = await extractor.extract_batch(classification, documents)
        
        return ClaimGenerationResponse(
            classification=classification,
            extraction=extraction
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

