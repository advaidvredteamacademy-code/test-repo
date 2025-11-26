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
    logger.info(f"Extraction complete: {extraction.successful_extractions} successful, {extraction.failed_extractions} failed")
    
    return ClaimGenerationResponse(
        classification=classification,
        extraction=extraction
    )

