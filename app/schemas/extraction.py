from pydantic import BaseModel, Field
from typing import Optional, List

class BillExtraction(BaseModel):
    hospital_name: Optional[str] = Field(None, description="Name of the hospital or medical facility")
    patient_name: Optional[str] = Field(None, description="Name of the patient")
    bill_number: Optional[str] = Field(None, description="Bill or invoice number")
    bill_date: Optional[str] = Field(None, description="Date of the bill")
    admission_date: Optional[str] = Field(None, description="Admission date if applicable")
    discharge_date: Optional[str] = Field(None, description="Discharge date if applicable")
    total_amount: Optional[float] = Field(None, description="Total bill amount")
    paid_amount: Optional[float] = Field(None, description="Amount paid")
    balance_amount: Optional[float] = Field(None, description="Balance or outstanding amount")
    items: Optional[List[str]] = Field(None, description="List of billed items or services")

class DischargeSummaryExtraction(BaseModel):
    patient_name: Optional[str] = Field(None, description="Name of the patient")
    patient_age: Optional[str] = Field(None, description="Age of the patient")
    patient_gender: Optional[str] = Field(None, description="Gender of the patient")
    admission_date: Optional[str] = Field(None, description="Date of admission")
    discharge_date: Optional[str] = Field(None, description="Date of discharge")
    hospital_name: Optional[str] = Field(None, description="Name of the hospital")
    doctor_name: Optional[str] = Field(None, description="Name of the treating doctor")
    diagnosis: Optional[str] = Field(None, description="Primary diagnosis or condition")
    procedures_performed: Optional[List[str]] = Field(None, description="List of procedures or treatments performed")
    medications: Optional[List[str]] = Field(None, description="List of medications prescribed")


class IDCardExtraction(BaseModel):
    id_type: Optional[str] = Field(None, description="Type of ID (Aadhar, PAN, Driver's License, etc.)")
    id_number: Optional[str] = Field(None, description="ID card number")
    name: Optional[str] = Field(None, description="Name on the ID card")
    date_of_birth: Optional[str] = Field(None, description="Date of birth")
    gender: Optional[str] = Field(None, description="Gender")
    address: Optional[str] = Field(None, description="Address on the ID card")
    issue_date: Optional[str] = Field(None, description="Date of issue")
    expiry_date: Optional[str] = Field(None, description="Date of expiry if applicable")

class PharmacyBillExtraction(BaseModel):
    pharmacy_name: Optional[str] = Field(None, description="Name of the pharmacy")
    pharmacy_address: Optional[str] = Field(None, description="Address of the pharmacy")
    bill_number: Optional[str] = Field(None, description="Bill or receipt number")
    bill_date: Optional[str] = Field(None, description="Date of the bill")
    patient_name: Optional[str] = Field(None, description="Name of the patient if available")
    doctor_name: Optional[str] = Field(None, description="Name of the prescribing doctor if available")
    medicines: Optional[List[dict]] = Field(None, description="List of medicines with name, quantity, and price")
    total_amount: Optional[float] = Field(None, description="Total bill amount")
    discount: Optional[float] = Field(None, description="Discount applied if any")
    paid_amount: Optional[float] = Field(None, description="Final amount paid")

class ClaimFormExtraction(BaseModel):
    claim_number: Optional[str] = Field(None, description="Claim form number")
    policy_number: Optional[str] = Field(None, description="Insurance policy number")
    patient_name: Optional[str] = Field(None, description="Name of the insured/patient")
    date_of_claim: Optional[str] = Field(None, description="Date of claim submission")
    date_of_incident: Optional[str] = Field(None, description="Date of medical incident or treatment")
    hospital_name: Optional[str] = Field(None, description="Name of the hospital where treatment was received")
    claimed_amount: Optional[float] = Field(None, description="Amount claimed")
    diagnosis: Optional[str] = Field(None, description="Diagnosis or reason for claim")
    treatment_details: Optional[str] = Field(None, description="Details of treatment received")
    insurer_name: Optional[str] = Field(None, description="Name of the insurance company")

class ExtractionResult(BaseModel):
    filename: str = Field(description="Document filename", exclude=True)
    document_type: str = Field(description="Type of document")
    extraction_status: str = Field(description="Status: success or failed")
    extracted_data: Optional[dict] = Field(None, description="Extracted data specific to document type")
    error_message: Optional[str] = Field(None, description="Error message if extraction failed")

class ExtractionResponse(BaseModel):
    results: List[ExtractionResult] = Field(description="List of extraction results")
    total_extracted: int = Field(description="Total number of documents extracted")

