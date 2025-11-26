from pydantic import BaseModel, Field
from .document import DocumentType

class DocumentInfo(BaseModel):
    document_file_name: str = Field(description="Exact document filename from uploaded files", exclude=True)
    document_type: DocumentType = Field(description="Type of document identified")
    confidence: float = Field(description="Confidence score between 0 and 100", ge=0.0, le=100.0)
    present: bool = Field(description="Whether the document is present")
    reason: str = Field(description="Brief explanation for the classification")

class ClassificationResult(BaseModel):
    BILL: DocumentInfo = Field(description="Hospital or medical bill information")
    DISCHARGE_SUMMARY: DocumentInfo = Field(description="Patient discharge summary information")
    ID_CARD: DocumentInfo = Field(description="Identity card information")
    PHARMACY_BILL: DocumentInfo = Field(description="Pharmacy or medicine bill information")
    CLAIM_FORM: DocumentInfo = Field(description="Insurance claim form information")

