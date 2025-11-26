# SuperClaims API

A FastAPI-based document processing system for insurance claims, utilizing LangChain and Google's Gemini AI for document classification and data extraction.

## Features

- **Document Classification**: Automatically classifies uploaded documents into categories (Bill, Discharge Summary, ID Card, Pharmacy Bill, Claim Form)
- **Data Extraction**: Extracts structured data from classified documents using LLM-powered agents
- **Parallel Processing**: Concurrent document loading and extraction for optimal performance
- **RESTful API**: Clean FastAPI endpoints with proper error handling and validation

## Project Structure

```
test1/
├── app/
│   ├── api/                  # API routes and endpoints
│   │   ├── deps.py          # Dependency injection
│   │   └── v1/
│   │       └── endpoints/   # API endpoint modules
│   ├── agents/              # LangChain agents
│   │   ├── classification.py
│   │   └── extraction.py
│   ├── core/                # Core functionality
│   │   ├── llm.py          # LLM initialization
│   │   └── prompts.py      # Prompt templates
│   ├── schemas/             # Pydantic models
│   │   ├── classification.py
│   │   ├── extraction.py
│   │   └── document.py
│   ├── services/            # Business logic
│   │   └── document_loader.py
│   ├── config.py           # Application settings
│   ├── exceptions.py       # Custom exceptions
│   └── main.py            # FastAPI application
├── uploaded_documents/     # Document storage
├── requirements.txt
└── .env
```

## Installation

1. Clone the repository and navigate to the project directory

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your Google API key:
```
GOOGLE_API_KEY=your_api_key_here
```

## Running the Application

Development mode with auto-reload:
```bash
python -m app.main
```

Or using uvicorn directly:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### Health Check
```
GET /api/v1/
```

### Generate Claim
```
POST /api/v1/generate-claim
```
Upload documents for classification and extraction.

**Request**: Multipart form data with files

**Response**:
```json
{
  "classification": {
    "BILL": {...},
    "DISCHARGE_SUMMARY": {...},
    ...
  },
  "extraction": {
    "results": [...],
    "total_extracted": 3,
    "successful_extractions": 3,
    "failed_extractions": 0
  }
}
```

## Configuration

All configuration is managed through `app/config.py` using pydantic-settings:

- `GOOGLE_API_KEY`: Your Google Gemini API key
- `LLM_MODEL`: Model to use (default: gemini-2.5-flash)
- `MAX_FILE_SIZE`: Maximum upload size (default: 10MB)
- `ALLOWED_FILE_TYPES`: Supported file extensions

## Architecture Highlights

- **Dependency Injection**: FastAPI's dependency system for clean separation of concerns
- **Async Processing**: Concurrent document loading and extraction
- **Structured Outputs**: LangChain structured output for reliable data extraction
- **Error Handling**: Custom exceptions with proper HTTP status codes
- **Caching**: LLM instance caching for performance optimization

## Development

The codebase follows FastAPI and LangChain best practices:
- Proper module organization
- Type hints throughout
- Pydantic models for validation
- Async/await for I/O operations
- Dependency injection pattern

