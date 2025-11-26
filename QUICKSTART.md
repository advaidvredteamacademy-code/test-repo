# Quick Start Guide

## Prerequisites
- Python 3.9+
- Google Gemini API Key

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file in the project root:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 3. Run the Application
```bash
# Using Python module
python3 -m app.main

# Or using uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Access API Documentation
Open your browser and navigate to:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing the API

### Using curl
```bash
curl -X POST "http://localhost:8000/api/v1/generate-claim" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@/path/to/document1.pdf" \
  -F "files=@/path/to/document2.pdf"
```

### Using Python requests
```python
import requests

url = "http://localhost:8000/api/v1/generate-claim"
files = [
    ("files", open("document1.pdf", "rb")),
    ("files", open("document2.pdf", "rb"))
]

response = requests.post(url, files=files)
print(response.json())
```

### Response Format
```json
{
  "classification": {
    "BILL": {
      "document_file_name": "doc_1.pdf",
      "document_type": "BILL",
      "confidence": 0.95,
      "present": true,
      "reason": "Contains hospital billing information"
    },
    ...
  },
  "extraction": {
    "results": [
      {
        "filename": "doc_1.pdf",
        "document_type": "BILL",
        "extraction_status": "success",
        "extracted_data": {
          "hospital_name": "City Hospital",
          "patient_name": "John Doe",
          ...
        }
      }
    ],
    "total_extracted": 1,
    "successful_extractions": 1,
    "failed_extractions": 0
  }
}
```

## Project Structure Overview

```
app/
├── main.py                    # FastAPI application entry point
├── config.py                  # Configuration settings
├── exceptions.py              # Custom exception handlers
│
├── api/                       # API layer
│   ├── deps.py               # Dependency injection
│   └── v1/endpoints/         # Version 1 endpoints
│       ├── health.py         # Health check
│       └── claims.py         # Claims processing
│
├── core/                      # Core functionality
│   ├── llm.py                # LLM initialization
│   └── prompts.py            # Prompt templates
│
├── schemas/                   # Data models
│   ├── document.py           # Document enums
│   ├── classification.py     # Classification models
│   └── extraction.py         # Extraction models
│
├── agents/                    # LangChain agents
│   ├── classification.py     # Document classifier
│   └── extraction.py         # Data extractor
│
└── services/                  # Business logic
    └── document_loader.py    # Document loading service
```

## Common Tasks

### Add a New Document Type
1. Add enum to `app/schemas/document.py`
2. Add extraction model to `app/schemas/extraction.py`
3. Add to `EXTRACTION_MODELS` in `app/agents/extraction.py`
4. Add prompt to `app/core/prompts.py`

### Add a New Endpoint
1. Create new file in `app/api/v1/endpoints/`
2. Add router to `app/api/v1/__init__.py`
3. Define request/response models in schemas

### Modify LLM Settings
Edit `app/config.py`:
```python
LLM_MODEL: str = "gemini-2.5-flash"
LLM_TEMPERATURE: float = 0.0
LLM_MAX_RETRIES: int = 3
```

## Troubleshooting

### Module Not Found Error
```bash
# Make sure you're in the project root
cd /path/to/test1

# Run with python -m
python3 -m app.main
```

### GOOGLE_API_KEY Error
- Ensure `.env` file exists in project root
- Check API key is valid
- Verify key has necessary permissions

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Port Already in Use
```bash
# Use a different port
uvicorn app.main:app --port 8001
```

## Development Tips

### Enable Debug Mode
In `.env` or `app/config.py`:
```python
DEBUG: bool = True
LOG_LEVEL: str = "DEBUG"
```

### View Logs
Logs are printed to console with timestamps:
```
2025-11-26 10:30:15 - app.agents.classification - INFO - Starting classification...
```

### API Documentation
FastAPI auto-generates interactive docs at `/docs` - use this to:
- Test endpoints
- View request/response schemas
- Understand API structure

## Next Steps

- Read `IMPROVEMENTS.md` for detailed refactoring notes
- Check `README.md` for architecture details
- Explore the codebase starting from `app/main.py`

