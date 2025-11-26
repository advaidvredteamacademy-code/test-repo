from enum import Enum
from typing import List

class DocumentType(str, Enum):
    BILL = "BILL"
    DISCHARGE_SUMMARY = "DISCHARGE_SUMMARY"
    ID_CARD = "ID_CARD"
    PHARMACY_BILL = "PHARMACY_BILL"
    CLAIM_FORM = "CLAIM_FORM"

# Define required documents for claim validation
REQUIRED_DOCUMENTS: List[DocumentType] = [
    DocumentType.BILL,
    DocumentType.DISCHARGE_SUMMARY,
    DocumentType.ID_CARD,
    DocumentType.CLAIM_FORM
]

def get_required_document_types() -> List[str]:
    """Returns list of required document type names as strings"""
    return [doc.value for doc in REQUIRED_DOCUMENTS]

