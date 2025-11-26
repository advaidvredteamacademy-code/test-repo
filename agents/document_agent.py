
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from dotenv import load_dotenv
import os

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Define document types as Enum
class DocumentType(str, Enum):
    BILL = "BILL"
    DISCHARGE_SUMMARY = "DISCHARGE_SUMMARY"
    ID_CARD = "ID_CARD"
    PHARMACY_BILL = "PHARMACY_BILL"
    CLAIM_FORM = "CLAIM_FORM"

# Individual document classification
class DocumentInfo(BaseModel):
    """A single classified document."""
    document_file_name: str = Field(description="exact Document file name from the uploaded files(metadata)")
    document_type: DocumentType = Field(description="The type of document identified")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0", ge=0.0, le=1.0)
    present: bool = Field(description="Whether the document is present")
    reason: str = Field(description="Brief explanation for the classification")

class ClassificationResult(BaseModel):
    """Classification result for all document types."""
    BILL: DocumentInfo = Field(description="Hospital or medical bill information")
    DISCHARGE_SUMMARY: DocumentInfo = Field(description="Patient discharge summary information")
    ID_CARD: DocumentInfo = Field(description="Identity card information")
    PHARMACY_BILL: DocumentInfo = Field(description="Pharmacy or medicine bill information")
    CLAIM_FORM: DocumentInfo = Field(description="Insurance claim form information")

from services import model

# Bind structured output
structured_model = model.with_structured_output(ClassificationResult)

# Example usage
def classify_documents(all_documents) -> ClassificationResult:
    """
    Classify multiple documents and return structured results.
    
    Args:
        all_documents: List of all documents
    
    Returns:
        Document with the classification result
    """
    # Create prompt with metadata 
    documents_text = "\n\n".join([
        f"Source: {doc.metadata.get('source', 'Unknown')}, Page: {doc.metadata.get('page', 'Unknown')}\n{doc.page_content}"
        for doc in all_documents
    ])
    prompt = f"""Analyze and classify the following documents. For EACH of these 5 categories, determine if it's present:

1. BILL: Hospital or medical bills
2. DISCHARGE_SUMMARY: Patient discharge summaries
3. ID_CARD: Identity cards (Aadhar, PAN, Driver's License, etc.)
4. PHARMACY_BILL: Pharmacy or medicine bills
5. CLAIM_FORM: Insurance claim forms

Documents:
{documents_text}

For EACH document type (all 5), you must specify:
- present: true if this type exists, false otherwise
- filename: the actual filename if present, null if not present
- confidence: score between 0.0-1.0 if present, null if not present
- reason: brief explanation if present, null if not present

Important: Return information for ALL 5 document types, even if some are not present.
"""
    
    result = structured_model.invoke(prompt)
    return result