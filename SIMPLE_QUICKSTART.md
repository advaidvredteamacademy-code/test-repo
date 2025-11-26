# Simple Quick Start Guide

## Setup (3 Steps)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set API Key
```bash
export GOOGLE_API_KEY="your-gemini-api-key-here"
```

### 3. Run Server
```bash
python3 -m app.main
```

That's it! Server runs at `http://localhost:8000`

---

## API Endpoints

### Health Check
```bash
curl http://localhost:8000/
```

Response:
```json
{
  "status": "healthy",
  "message": "API is running"
}
```

### Generate Claim
```bash
curl -X POST "http://localhost:8000/generate-claim" \
  -F "files=@document1.pdf" \
  -F "files=@document2.pdf"
```

---

## Project Structure (Simple!)

```
app/
├── main.py              # FastAPI app (24 lines)
├── config.py            # Settings (17 lines)
├── api/
│   ├── claims.py        # Main endpoint
│   ├── health.py        # Health check
│   └── deps.py          # Dependency injection
├── agents/
│   ├── classification.py  # Document classifier
│   └── extraction.py      # Data extractor
├── services/
│   └── document_loader.py # PDF loader
├── schemas/             # Pydantic models
└── core/                # LLM setup & prompts
```

---

## How It Works (Simple Explanation)

1. **Upload** → User sends PDF files
2. **Load** → Extract text from PDFs
3. **Classify** → AI identifies document types (bill, discharge summary, etc.)
4. **Extract** → AI extracts structured data from each document
5. **Return** → Send back JSON with all extracted information

---

## Testing with Swagger UI

1. Start the server
2. Open `http://localhost:8000/docs`
3. Click "POST /generate-claim"
4. Click "Try it out"
5. Upload PDFs
6. Click "Execute"

---

## Code Flow Example

```python
# 1. Request comes in
POST /generate-claim with files

# 2. Load documents
documents = await loader.load_documents(files)

# 3. Classify document types
classification = await classifier.classify(documents)

# 4. Extract data in parallel
extraction = await extractor.extract_batch(classification, documents)

# 5. Return results
return {classification, extraction}
```

---

## Common Issues

**Q: ImportError: No module named 'fastapi'**  
A: Run `pip install -r requirements.txt`

**Q: Error: GOOGLE_API_KEY not set**  
A: Set it: `export GOOGLE_API_KEY="your-key"`

**Q: Can't upload files**  
A: Only PDFs are supported, max 10MB

---

## Making Changes

### Add a new document type:
1. Add to `schemas/document.py` → DocumentType enum
2. Add schema to `schemas/extraction.py`
3. Add to `agents/extraction.py` → EXTRACTION_MODELS
4. Add prompt to `core/prompts.py`

### Change LLM model:
```python
# In config.py
LLM_MODEL: str = "gemini-1.5-pro"  # or any other model
```

### Add authentication:
```python
# In api/claims.py
from fastapi.security import HTTPBearer

security = HTTPBearer()

@router.post("/generate-claim")
async def generate_claim(
    credentials: str = Depends(security),
    # ... rest of params
):
    # Your code
```

---

## Key Files to Understand

1. **`app/main.py`** - Entry point, sets up FastAPI
2. **`app/api/claims.py`** - Main endpoint logic
3. **`app/agents/classification.py`** - How AI classifies documents
4. **`app/agents/extraction.py`** - How AI extracts data
5. **`app/schemas/`** - Data models (what data looks like)

---

## Questions for Your Assignment

See `ASSIGNMENT_QUESTIONS.md` for common questions and answers!

---

## Want More Details?

- `SIMPLIFICATION_SUMMARY.md` - What was changed
- `BEFORE_AFTER_COMPARISON.md` - Before/after code comparison
- `ASSIGNMENT_QUESTIONS.md` - Q&A for presentations
- `QUICKSTART.md` - Original detailed guide

