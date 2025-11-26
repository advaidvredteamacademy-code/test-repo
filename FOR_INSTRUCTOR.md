# Project Overview - Insurance Claim Processing API

## What This Project Does

This is a FastAPI-based REST API that uses AI (Google Gemini) to automatically process insurance claim documents. It can:

1. **Accept multiple PDF documents** (bills, discharge summaries, ID cards, etc.)
2. **Classify document types** using AI
3. **Extract structured data** from each document type
4. **Return JSON responses** with all extracted information

---

## Technology Stack

- **Framework**: FastAPI (Python web framework)
- **AI/LLM**: Google Gemini (via LangChain)
- **Document Processing**: PyPDF, LangChain
- **Async Processing**: Python asyncio
- **Data Validation**: Pydantic

---

## Key Features

### 1. Asynchronous Processing
- Multiple documents processed in parallel
- Non-blocking LLM API calls
- Efficient handling of concurrent requests

### 2. Structured Output
- AI returns validated data matching predefined schemas
- Type-safe data extraction
- Automatic validation of extracted fields

### 3. Multiple Document Types
Supports 5 document types:
- Hospital Bills
- Discharge Summaries
- Insurance ID Cards
- Pharmacy Bills
- Claim Forms

Each has a custom extraction schema with relevant fields.

### 4. Intelligent Classification
AI automatically identifies:
- Which document is which type
- Which documents are present/absent
- Which file contains which document

---

## Project Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ POST /generate-claim (PDFs)
       ▼
┌─────────────────────────────────┐
│   FastAPI (app/main.py)         │
│   - Routes                      │
│   - CORS Middleware             │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│   API Layer (app/api/)          │
│   - claims.py (main endpoint)   │
│   - health.py (health check)    │
└────────┬────────────────────────┘
         │
    ┌────┴────┬─────────────┐
    ▼         ▼             ▼
┌────────┐ ┌──────────┐ ┌──────────┐
│ Loader │ │Classifier│ │Extractor │
│Service │ │  Agent   │ │  Agent   │
└────────┘ └──────────┘ └──────────┘
    │           │            │
    │           └────┬───────┘
    │                ▼
    │         ┌──────────────┐
    │         │ LLM (Gemini) │
    │         └──────────────┘
    ▼
┌────────────┐
│ File System│
└────────────┘
```

---

## API Usage

### Endpoint: `POST /generate-claim`

**Request:**
```bash
curl -X POST "http://localhost:8000/generate-claim" \
  -F "files=@bill.pdf" \
  -F "files=@discharge_summary.pdf"
```

**Response:**
```json
{
  "classification": {
    "bill": {
      "present": true,
      "document_file_name": "doc_1.pdf"
    },
    "discharge_summary": {
      "present": true,
      "document_file_name": "doc_2.pdf"
    },
    "id_card": {
      "present": false,
      "document_file_name": null
    }
    // ... other types
  },
  "extraction": {
    "results": [
      {
        "filename": "doc_1.pdf",
        "document_type": "bill",
        "extraction_status": "success",
        "extracted_data": {
          "hospital_name": "City Hospital",
          "total_amount": 15000.00,
          "items": [...]
        }
      }
    ],
    "total_extracted": 2,
    "successful_extractions": 2,
    "failed_extractions": 0
  }
}
```

---

## Code Highlights

### 1. Dependency Injection Pattern
```python
# app/api/deps.py
def get_document_loader() -> DocumentLoaderService:
    return DocumentLoaderService()

DocumentLoaderDep = Annotated[
    DocumentLoaderService, 
    Depends(get_document_loader)
]
```

### 2. Structured Output from LLM
```python
# app/agents/classification.py
self.structured_llm = self.llm.with_structured_output(ClassificationResult)
result = await loop.run_in_executor(None, self.structured_llm.invoke, prompt)
```

### 3. Parallel Async Processing
```python
# app/agents/extraction.py
tasks = [self.extract_single(...) for doc in documents]
results = await asyncio.gather(*tasks)  # All run in parallel
```

---

## Design Decisions

### Why FastAPI?
- Modern Python framework with async support
- Automatic API documentation (Swagger UI)
- Built-in type validation
- High performance for I/O operations

### Why Async?
- LLM calls take 1-3 seconds each
- Async allows processing multiple documents simultaneously
- Better resource utilization
- Scalable for multiple users

### Why Structured Output?
- Ensures consistent data format
- Automatic validation
- Type safety
- Easier to work with in frontend

### Why LangChain?
- Abstracts LLM API complexity
- Built-in retry logic
- Easy to switch between LLM providers
- Structured output support

---

## Implementation Complexity

### Simple Parts:
- ✅ API endpoint setup (FastAPI makes this easy)
- ✅ File upload handling (built into FastAPI)
- ✅ PDF text extraction (using existing library)

### Complex Parts:
- ⚡ **Prompt Engineering**: Crafting prompts that reliably extract correct data
- ⚡ **Schema Design**: Defining Pydantic models for each document type
- ⚡ **Async Coordination**: Managing parallel LLM calls without race conditions
- ⚡ **Error Handling**: Gracefully handling partial failures

---

## Testing the Application

### 1. Interactive API Docs
Visit `http://localhost:8000/docs` for Swagger UI

### 2. Health Check
```bash
curl http://localhost:8000/
```

### 3. Sample Request
```bash
curl -X POST "http://localhost:8000/generate-claim" \
  -F "files=@/path/to/sample.pdf"
```

---

## Configuration

All settings in `app/config.py`:

```python
class Settings(BaseSettings):
    APP_NAME: str = "Insurance Claim Processing API"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    GOOGLE_API_KEY: str          # Required
    LLM_MODEL: str = "gemini-2.5-flash"
    LLM_TEMPERATURE: float = 0.0 # Deterministic output
    
    UPLOAD_DIR: str = "uploaded_documents"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
```

---

## Scalability Considerations

### Current Capacity:
- Can handle multiple concurrent requests (async)
- Limited by LLM API rate limits (typically 10-60 req/min)
- File storage is local (not production-ready)

### For Production:
1. Add database for tracking submissions
2. Use object storage (S3) instead of local files
3. Add job queue (Celery) for background processing
4. Add caching for repeated documents
5. Add rate limiting and authentication
6. Monitor LLM costs and latency

---

## Code Quality

### Strengths:
- ✅ Type hints throughout
- ✅ Pydantic for validation
- ✅ Clean separation of concerns (API/Service/Agent layers)
- ✅ Async/await for I/O operations
- ✅ Dependency injection pattern
- ✅ RESTful API design

### Intentional Simplifications (for assignment):
- Removed complex exception handling
- Removed verbose logging
- Removed API versioning
- Simple error messages (not production-grade)

---

## Learning Outcomes

This project demonstrates:
1. **API Development**: Building RESTful APIs with FastAPI
2. **AI Integration**: Using LLMs for structured data extraction
3. **Async Programming**: Managing concurrent operations
4. **Software Architecture**: Layered application design
5. **Data Validation**: Using Pydantic for type safety
6. **Cloud Services**: Integrating external APIs (Gemini)

---

## Future Enhancements

1. **OCR Support**: Handle scanned documents (images)
2. **Confidence Scores**: Show AI confidence for each extraction
3. **Multi-language**: Support documents in different languages
4. **Audit Trail**: Log all processing steps
5. **User Authentication**: Add login/sessions
6. **Web Interface**: Simple upload form (currently API-only)
7. **Batch Processing**: Process large volumes via queue

---

## Documentation Files

- `SIMPLE_QUICKSTART.md` - Quick setup guide
- `ASSIGNMENT_QUESTIONS.md` - Common Q&A for presentations
- `BEFORE_AFTER_COMPARISON.md` - Code simplification details
- `SIMPLIFICATION_SUMMARY.md` - What was simplified and why
- `QUICKSTART.md` - Detailed original documentation
- `ARCHITECTURE.md` - System architecture details

---

## Running the Project

```bash
# 1. Install
pip install -r requirements.txt

# 2. Set API key
export GOOGLE_API_KEY="your-key"

# 3. Run
python3 -m app.main

# 4. Test
open http://localhost:8000/docs
```

---

## Summary

This is a production-quality API (simplified for assignment) that demonstrates:
- Modern Python web development
- AI/LLM integration
- Async programming
- Clean architecture
- Type-safe code

The simplifications make it easier to understand and explain while maintaining all core functionality.

