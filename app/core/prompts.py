from app.schemas.document import DocumentType

CLASSIFICATION_PROMPT = """Analyze and classify the following documents. For EACH of these 5 categories, determine if it's present:

1. BILL: Hospital or medical bills
2. DISCHARGE_SUMMARY: Patient discharge summaries
3. ID_CARD: Identity cards (Aadhar, PAN, Driver's License, etc.)
4. PHARMACY_BILL: Pharmacy or medicine bills
5. CLAIM_FORM: Insurance claim forms

Documents:
{documents_text}

For EACH document type (all 5), you must specify:
- present: true if this type exists, false otherwise
- filename: the actual filename if present
- confidence: score between 0.0-1.0 if present
- reason: brief explanation if present

Important: Return information for ALL 5 document types, even if some are not present."""

EXTRACTION_PROMPTS = {
    DocumentType.BILL: """Extract all relevant information from this medical bill document.
Focus on extracting:
- Hospital/facility name
- Patient name
- Bill number and date
- Admission and discharge dates
- Amount details (total, paid, balance)
- List of billed items or services

Document content:
{content}

Extract as much information as possible. If a field is not found, leave it as null.""",

    DocumentType.DISCHARGE_SUMMARY: """Extract all relevant information from this discharge summary document.
Focus on extracting:
- Patient demographics (name, age, gender)
- Admission and discharge dates
- Hospital and doctor name
- Diagnosis
- Procedures performed
- Medications prescribed
- Follow-up instructions

Document content:
{content}

Extract as much information as possible. If a field is not found, leave it as null.""",

    DocumentType.ID_CARD: """Extract all relevant information from this ID card document.
Focus on extracting:
- Type of ID card
- ID number
- Name
- Date of birth
- Gender
- Address
- Issue and expiry dates

Document content:
{content}

Extract as much information as possible. If a field is not found, leave it as null.""",

    DocumentType.PHARMACY_BILL: """Extract all relevant information from this pharmacy bill document.
Focus on extracting:
- Pharmacy name and address
- Bill number and date
- Patient and doctor names
- List of medicines with details
- Amount details (total, discount, paid)

Document content:
{content}

Extract as much information as possible. If a field is not found, leave it as null.""",

    DocumentType.CLAIM_FORM: """Extract all relevant information from this insurance claim form document.
Focus on extracting:
- Claim and policy numbers
- Patient name
- Claim and incident dates
- Hospital name
- Claimed amount
- Diagnosis and treatment details
- Insurer name

Document content:
{content}

Extract as much information as possible. If a field is not found, leave it as null.""",
}

UNIFIED_FAST_CLAIM_PROMPT = """You are an expert insurance claim processor. Analyze ALL the provided documents and perform BOTH classification AND extraction in a single pass.

Documents:
{documents_text}

Your task is to:
1. CLASSIFY each of the 5 document types (BILL, DISCHARGE_SUMMARY, ID_CARD, PHARMACY_BILL, CLAIM_FORM):
   - Determine if each type is present in the uploaded documents
   - Provide the exact filename for each present document
   - Give a confidence score (0-100) for each present document
   - Explain your reasoning for each classification

2. EXTRACT detailed information from EACH document that is present:
   
   For BILL documents, extract:
   - Hospital/facility name, Patient name
   - Bill number, bill date, admission date, discharge date
   - Amount details (total, paid, balance)
   - List of billed items or services
   
   For DISCHARGE_SUMMARY documents, extract:
   - Patient demographics (name, age, gender)
   - Admission and discharge dates
   - Hospital and doctor name
   - Diagnosis, Procedures performed, Medications prescribed
   
   For ID_CARD documents, extract:
   - Type of ID card, ID number, Name
   - Date of birth, Gender, Address
   - Issue and expiry dates
   
   For PHARMACY_BILL documents, extract:
   - Pharmacy name and address
   - Bill number and date
   - Patient and doctor names
   - List of medicines with details
   - Amount details (total, discount, paid)
   
   For CLAIM_FORM documents, extract:
   - Claim and policy numbers, Patient name
   - Claim and incident dates
   - Hospital name, Claimed amount
   - Diagnosis and treatment details, Insurer name

IMPORTANT:
- You MUST provide classification info for ALL 5 document types (even if not present, set present=false)
- You MUST extract data for EVERY document type that is present
- If a field is not found, set it to null
- Be thorough and accurate in your extraction"""

