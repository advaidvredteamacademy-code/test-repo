# Potential Assignment Questions & Answers

This document contains common questions you might be asked about your project and how to answer them.

## Architecture & Design Questions

### Q: Explain the overall architecture of your application.
**A**: This is a FastAPI-based REST API that processes insurance claim documents. It has three main layers:
1. **API Layer** (`app/api/`) - Handles HTTP requests/responses
2. **Service Layer** (`app/services/`) - Handles document loading and file operations
3. **Agent Layer** (`app/agents/`) - Contains the AI logic for classification and extraction

### Q: Why did you choose FastAPI?
**A**: FastAPI provides:
- Built-in async support for handling multiple document uploads
- Automatic API documentation with Swagger UI
- Type validation using Pydantic
- Good performance for I/O-bound operations like LLM calls

### Q: How does the document processing pipeline work?
**A**: 
1. User uploads PDF files via POST request to `/generate-claim`
2. `DocumentLoaderService` validates and saves files, then extracts text
3. `DocumentClassifier` identifies document types (bill, discharge summary, etc.)
4. `DocumentExtractor` extracts structured data from each document type
5. Results are returned as JSON

## Technical Implementation Questions

### Q: How do you handle concurrent document processing?
**A**: I use Python's `asyncio` for async/await patterns:
- File uploads are processed in parallel using `asyncio.gather()`
- LLM calls are wrapped with `run_in_executor()` since they're blocking operations
- Multiple extractions run concurrently for different document types

### Q: How does the LLM integration work?
**A**: I use LangChain with Google's Gemini model:
- `with_structured_output()` ensures the LLM returns data matching our Pydantic schemas
- For classification: single prompt with all documents
- For extraction: separate prompts for each document type with specific schemas

### Q: What is dependency injection in your code?
**A**: In `app/api/deps.py`, I define dependencies that FastAPI injects:
```python
DocumentLoaderDep = Annotated[DocumentLoaderService, Depends(get_document_loader)]
```
This creates instances once per request and makes testing easier.

### Q: How do you ensure data validation?
**A**: Using Pydantic models:
- Input validation: UploadFile validation for file type and size
- Output validation: Structured schemas for classification and extraction results
- LLM validation: `with_structured_output()` forces LLM to match the schema

## Code-Specific Questions

### Q: Explain the document classification process.
**A**: 
1. Combine all uploaded documents into a single text with metadata
2. Send to LLM with a prompt asking to identify document types
3. LLM returns a `ClassificationResult` with fields for each possible document type
4. Each field indicates if that document type is present and which file it's in

### Q: How does parallel extraction work?
**A**: In `extract_batch()`:
1. Loop through all document types from classification
2. Create an async task for each present document type
3. Use `asyncio.gather()` to run all extractions in parallel
4. Collect results and return statistics (successful/failed)

### Q: What happens if extraction fails for one document?
**A**: Each extraction is wrapped in try-except:
- Failures are caught and returned as `ExtractionResult` with status="failed"
- Other documents continue processing
- The response shows which succeeded and which failed

### Q: How do you prevent memory issues with large files?
**A**: 
- Maximum file size limit (10MB in config)
- Files are processed page by page using PyPDFLoader
- Streaming file upload using `UploadFile`

## Design Decisions

### Q: Why use separate schemas for different document types?
**A**: Each document type has different fields:
- Bills need item-wise breakdowns
- Discharge summaries need diagnosis and treatment
- This gives better accuracy than a generic schema

### Q: Why async instead of synchronous code?
**A**: 
- LLM calls take 1-3 seconds each
- With async, we can process multiple documents simultaneously
- Better scalability for multiple concurrent users

### Q: How would you add a new document type?
**A**:
1. Add to `DocumentType` enum in `app/schemas/document.py`
2. Create extraction schema in `app/schemas/extraction.py`
3. Add to `EXTRACTION_MODELS` dict in `app/agents/extraction.py`
4. Create prompt in `app/core/prompts.py`

### Q: How is error handling implemented?
**A**: Simple approach using HTTPException:
- File validation errors → 400 Bad Request
- Processing errors → 500 Internal Server Error
- Errors are caught and re-raised with descriptive messages

## Testing Questions

### Q: How would you test this application?
**A**:
1. **Unit tests**: Test individual functions (file validation, prompt formatting)
2. **Integration tests**: Test full pipeline with sample PDFs
3. **API tests**: Test endpoints with FastAPI TestClient
4. **Mocking**: Mock LLM calls to avoid API costs during testing

### Q: What edge cases need handling?
**A**:
- Empty/corrupted PDFs
- Documents with no text (scanned images)
- Multiple documents of the same type
- Very large files
- Missing required fields in extraction

## Deployment Questions

### Q: What environment variables are needed?
**A**:
- `GOOGLE_API_KEY` (required) - For Gemini LLM access
- `LLM_MODEL` (optional) - Default is "gemini-2.5-flash"
- `HOST` and `PORT` (optional) - Default is 0.0.0.0:8000

### Q: How would you deploy this in production?
**A**:
1. Use a production ASGI server like Gunicorn with Uvicorn workers
2. Add authentication/authorization
3. Add rate limiting
4. Use object storage (S3) instead of local file storage
5. Add monitoring and logging
6. Use environment-specific configs

### Q: What security considerations are there?
**A**:
- File type validation (only PDFs)
- File size limits
- Input sanitization through Pydantic
- CORS middleware for cross-origin requests
- API key stored in environment variables (not code)

## Performance Questions

### Q: What are potential bottlenecks?
**A**:
1. LLM API calls (1-3 seconds each)
2. PDF text extraction for large files
3. File I/O operations

**Solutions**: Async processing, parallel extraction, file size limits

### Q: How many requests can this handle?
**A**: Depends on LLM rate limits. With proper async handling:
- FastAPI can handle 1000+ req/sec
- Bottleneck is LLM API (typically 10-60 requests/min)
- Could add queuing system for high load

## Improvement Questions

### Q: What improvements could be made?
**A**:
1. Add caching for repeated documents
2. Add background job queue (Celery/Redis)
3. Add database for tracking submissions
4. Add OCR for scanned documents
5. Add confidence scores for extractions
6. Add audit logging
7. Add retry logic for failed LLM calls

### Q: How would you scale this?
**A**:
1. Horizontal scaling with load balancer
2. Separate service for document processing
3. Message queue for async processing
4. Caching layer (Redis)
5. CDN for static content

