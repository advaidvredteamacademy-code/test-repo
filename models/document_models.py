import enum
from typing import Optional
from pydantic import BaseModel, Field

class DocType(enum.Enum):
    BILL = "bill"
    DISCHARGE_SUMMARY = "discharge_summary"
    ID_CARD = "id_card"
    PHARMACY_BILL = "pharmacy_bill"
    CLAIM_FORM = "claim_form"
    UNKNOWN = "unknown"

class ClassificationResult(BaseModel):
    """Result of document classification"""
    filename: str = Field(description="Original filename of the document")
    document_type: Optional[str] = Field(None, description="Classified document type or None if invalid")
    confidence_score: Optional[float] = Field(None, description="Confidence score (0-1) or None if invalid", ge=0, le=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "filename": "temp1.pdf",
                "document_type": "bill",
                "confidence_score": 0.95
            }
        }

class ClassificationResponse(BaseModel):
    """Response containing all classified documents"""
    results: list[ClassificationResult] = Field(description="List of classification results for each document")
    total_documents: int = Field(description="Total number of documents processed")
    valid_documents: int = Field(description="Number of valid documents classified")
    invalid_documents: int = Field(description="Number of invalid/unclassified documents")