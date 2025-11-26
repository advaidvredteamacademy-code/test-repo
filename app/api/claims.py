from typing import List, Dict, Any
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from pydantic import BaseModel

from app.services.document_loader import DocumentLoaderService
from app.agents.classification import DocumentClassifier
from app.agents.extraction import DocumentExtractor
from app.agents.fast_claim import FastClaimGenerator
from app.schemas.classification import ClassificationResult
from app.schemas.extraction import ExtractionResponse
from app.schemas.fast_claim import UnifiedClaimResponse, DocumentOutput, Validation, ClaimDecision
from app.schemas.document import get_required_document_types

from app.config import settings

router = APIRouter()

def process_extraction_to_unified(classification: ClassificationResult, extraction: ExtractionResponse) -> UnifiedClaimResponse:
    """Convert classification and extraction results to unified response format"""
    documents_output = []
    missing_documents = []
    discrepancies = []
    
    # Process extraction results
    for result in extraction.results:
        if result.extraction_status == "success" and result.extracted_data:
            documents_output.append(DocumentOutput(
                document_type=result.document_type,
                extracted_data=result.extracted_data,
                confidence=100.0  # Default confidence for successful extraction
            ))
    
    # Check for missing required documents based on classification
    required_docs = get_required_document_types()
    for doc_type in required_docs:
        doc_present = any(d.document_type == doc_type for d in documents_output)
        if not doc_present:
            missing_documents.append(doc_type)
    
    # Check for discrepancies in extracted data
    patient_names = set()
    for doc in documents_output:
        data = doc.extracted_data
        if "patient_name" in data and data["patient_name"]:
            patient_names.add(data["patient_name"])
        elif "name" in data and data["name"]:
            patient_names.add(data["name"])
    
    if len(patient_names) > 1:
        discrepancies.append(f"Patient name mismatch across documents: {', '.join(patient_names)}")
    
    # Determine claim decision
    if missing_documents:
        status = "pending"
        reason = f"Missing required documents: {', '.join(missing_documents)}"
    elif discrepancies:
        status = "pending"
        reason = f"Data discrepancies found: {'; '.join(discrepancies)}"
    else:
        status = "approved"
        reason = "All documents consistent and complete"
    
    return UnifiedClaimResponse(
        documents=documents_output,
        validation=Validation(
            missing_documents=missing_documents,
            discrepancies=discrepancies
        ),
        claim_decision=ClaimDecision(
            status=status,
            reason=reason
        )
    )

@router.post("/generate-claim", response_model=UnifiedClaimResponse)
async def generate_claim(
    files: List[UploadFile] = File(...),
    password: str = Form(...)
) -> UnifiedClaimResponse:
    """Generate insurance claim from uploaded documents"""
    if settings.API_PASSWORD != password:
        raise HTTPException(status_code=401, detail="Invalid password")
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
        
        return process_extraction_to_unified(classification, extraction)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def process_fast_claim_to_unified(fast_result) -> UnifiedClaimResponse:
    """Convert fast claim result to unified response format"""
    documents_output = []
    missing_documents = []
    discrepancies = []
    
    # Map of document types to their classification and data fields
    doc_types = {
        "BILL": ("BILL_classification", "BILL_data"),
        "DISCHARGE_SUMMARY": ("DISCHARGE_SUMMARY_classification", "DISCHARGE_SUMMARY_data"),
        "ID_CARD": ("ID_CARD_classification", "ID_CARD_data"),
        "PHARMACY_BILL": ("PHARMACY_BILL_classification", "PHARMACY_BILL_data"),
        "CLAIM_FORM": ("CLAIM_FORM_classification", "CLAIM_FORM_data")
    }
    
    # Process each document type
    for doc_type, (class_field, data_field) in doc_types.items():
        classification = getattr(fast_result.result, class_field)
        extracted_data = getattr(fast_result.result, data_field)
        
        if classification.present and extracted_data:
            # Convert Pydantic model to dict
            data_dict = extracted_data.dict(exclude_none=True)
            documents_output.append(DocumentOutput(
                document_type=doc_type,
                extracted_data=data_dict,
                confidence=classification.confidence
            ))
    
    # Check for missing required documents
    required_docs = get_required_document_types()
    for doc_type in required_docs:
        classification = getattr(fast_result.result, f"{doc_type}_classification")
        if not classification.present:
            missing_documents.append(doc_type)
    
    # Check for discrepancies in patient names
    patient_names = set()
    for doc in documents_output:
        data = doc.extracted_data
        if "patient_name" in data and data["patient_name"]:
            patient_names.add(data["patient_name"])
        elif "name" in data and data["name"]:
            patient_names.add(data["name"])
    
    if len(patient_names) > 1:
        discrepancies.append(f"Patient name mismatch across documents: {', '.join(patient_names)}")
    
    # Check for date discrepancies
    admission_dates = set()
    discharge_dates = set()
    for doc in documents_output:
        data = doc.extracted_data
        if "admission_date" in data and data["admission_date"]:
            admission_dates.add(data["admission_date"])
        if "discharge_date" in data and data["discharge_date"]:
            discharge_dates.add(data["discharge_date"])
    
    if len(admission_dates) > 1:
        discrepancies.append(f"Admission date mismatch: {', '.join(admission_dates)}")
    if len(discharge_dates) > 1:
        discrepancies.append(f"Discharge date mismatch: {', '.join(discharge_dates)}")
    
    # Determine claim decision
    if missing_documents:
        status = "pending"
        reason = f"Missing required documents: {', '.join(missing_documents)}"
    elif discrepancies:
        status = "pending"
        reason = f"Data discrepancies found: {'; '.join(discrepancies)}"
    else:
        status = "approved"
        reason = "All documents consistent and complete"
    
    return UnifiedClaimResponse(
        documents=documents_output,
        validation=Validation(
            missing_documents=missing_documents,
            discrepancies=discrepancies
        ),
        claim_decision=ClaimDecision(
            status=status,
            reason=reason
        )
    )

@router.post("/generate-claim-fast", response_model=UnifiedClaimResponse)
async def generate_claim_fast(
    files: List[UploadFile] = File(...),
    password: str = Form(...)
) -> UnifiedClaimResponse:
    if settings.API_PASSWORD != password:
        raise HTTPException(status_code=401, detail="Invalid password")
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    try:
        # Load documents
        loader = DocumentLoaderService()
        documents = await loader.load_documents(files)
        
        # Generate claim with single unified request
        generator = FastClaimGenerator()
        result = await generator.generate_claim(documents)
        
        return process_fast_claim_to_unified(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

