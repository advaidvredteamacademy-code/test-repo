from enum import Enum

class DocumentType(str, Enum):
    BILL = "BILL"
    DISCHARGE_SUMMARY = "DISCHARGE_SUMMARY"
    ID_CARD = "ID_CARD"
    PHARMACY_BILL = "PHARMACY_BILL"
    CLAIM_FORM = "CLAIM_FORM"

