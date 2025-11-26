# Insurance Claim Processing API

A FastAPI-based system for processing insurance claims from document uploads (PDFs). The system uses LLM-powered agents to classify, extract, and validate insurance documents.

## Features

- **Document Loading**: Upload and process PDF documents
- **Classification**: Automatically classify documents (Bill, Discharge Summary, ID Card, Pharmacy Bill, Claim Form)
- **Data Extraction**: Extract structured data from classified documents
- **Validation**: Check for missing documents and data discrepancies
- **Claim Decision**: Automated approval/pending status based on validation

## Processing Workflows

The system offers two processing modes:

![Processing Workflows Comparison](unnamed.jpg)

### Traditional Mode (`/generate-claim`)
- Separate classification step
- Parallel extraction using multiple LLM calls
- More granular but slower processing

### Fast Mode (`/generate-claim-fast`)
- Unified classification and extraction in a single LLM call
- Uses extended thinking mode
- Faster and more efficient

## API Endpoints

- `POST /generate-claim` - Traditional processing mode
- `POST /generate-claim-fast` - Fast processing mode (recommended)
- `GET /health` - Health check endpoint

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables (API keys, passwords, etc.)

3. Run the server:
```bash
uvicorn app.main:app --reload
```

4. Access the API at `http://localhost:8000`

## Technology Stack

- **FastAPI** - Web framework
- **LLM Integration** - For document classification and extraction
- **PyPDF** - PDF processing
- **Pydantic** - Data validation

## Project Structure

```
app/
├── agents/          # LLM-powered agents (classification, extraction, fast claim)
├── api/             # API routes
├── core/            # Core utilities (LLM, prompts)
├── schemas/         # Pydantic models
└── services/        # Business logic services
```

