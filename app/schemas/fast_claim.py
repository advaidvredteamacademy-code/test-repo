from pydantic import BaseModel, Field
from typing import Optional

# Import the standard extraction schemas to ensure consistency across all endpoints
from app.schemas.extraction import (
    BillExtraction,
    DischargeSummaryExtraction,
    IDCardExtraction,
    PharmacyBillExtraction,
    ClaimFormExtraction
)

class DocumentClassificationInfo(BaseModel):
    document_file_name: str = Field(description="Exact document filename from uploaded files")
    confidence: float = Field(description="Confidence score between 0 and 100", ge=0.0, le=100.0)
    present: bool = Field(description="Whether the document is present")
    reason: str = Field(description="Brief explanation for the classification")

class ClassificationAndExtraction(BaseModel):
    # Classification for all 5 document types
    BILL_classification: DocumentClassificationInfo = Field(description="Hospital or medical bill classification")
    DISCHARGE_SUMMARY_classification: DocumentClassificationInfo = Field(description="Patient discharge summary classification")
    ID_CARD_classification: DocumentClassificationInfo = Field(description="Identity card classification")
    PHARMACY_BILL_classification: DocumentClassificationInfo = Field(description="Pharmacy or medicine bill classification")
    CLAIM_FORM_classification: DocumentClassificationInfo = Field(description="Insurance claim form classification")
    
    # Extracted data for each document type (only present if document was found)
    # Now using the same extraction schemas as the regular extraction endpoint for consistency
    BILL_data: Optional[BillExtraction] = Field(None, description="Extracted bill data if BILL is present")
    DISCHARGE_SUMMARY_data: Optional[DischargeSummaryExtraction] = Field(None, description="Extracted discharge summary data if present")
    ID_CARD_data: Optional[IDCardExtraction] = Field(None, description="Extracted ID card data if present")
    PHARMACY_BILL_data: Optional[PharmacyBillExtraction] = Field(None, description="Extracted pharmacy bill data if present")
    CLAIM_FORM_data: Optional[ClaimFormExtraction] = Field(None, description="Extracted claim form data if present")

class FastClaimResponse(BaseModel):
    result: ClassificationAndExtraction = Field(description="Combined classification and extraction results")
    thinking: Optional[str] = Field(None, description="LLM thinking process if available")

