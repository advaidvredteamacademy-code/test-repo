# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client (API Consumer)                    │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 │ HTTP Request
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI Application                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Middleware Layer                       │  │
│  │  • CORS Middleware                                        │  │
│  │  • Exception Handlers                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                 │                                │
│                                 ▼                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    API Router (v1)                        │  │
│  │  • /api/v1/                                               │  │
│  │  • /api/v1/generate-claim                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                 │                                │
│                                 ▼                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Dependency Injection Layer                   │  │
│  │  • DocumentLoaderService                                  │  │
│  │  • DocumentClassifier                                     │  │
│  │  • DocumentExtractor                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Service Layer │    │   Agent Layer   │    │   Core Layer    │
│                 │    │                 │    │                 │
│ • Document      │    │ • Classification│    │ • LLM Init      │
│   Loader        │    │   Agent         │    │ • Prompts       │
│ • File Handler  │    │ • Extraction    │    │ • Config        │
│ • Validation    │    │   Agent         │    │                 │
└────────┬────────┘    └────────┬────────┘    └────────┬────────┘
         │                      │                       │
         │                      └───────────┬───────────┘
         │                                  │
         ▼                                  ▼
┌─────────────────┐              ┌─────────────────────┐
│  File System    │              │  Google Gemini API  │
│                 │              │                     │
│ • PDF Storage   │              │ • Classification    │
│ • Document Mgmt │              │ • Extraction        │
└─────────────────┘              └─────────────────────┘
```

## Request Flow

### 1. Document Upload Request

```
Client
  │
  ├─ POST /api/v1/generate-claim
  │  └─ files: [document1.pdf, document2.pdf]
  │
  ▼
FastAPI Router
  │
  ├─ Validate request
  ├─ Inject dependencies
  │
  ▼
Claims Endpoint Handler
  │
  ├─ [1] DocumentLoaderService.load_documents()
  │     │
  │     ├─ Validate files (type, size)
  │     ├─ Save files concurrently
  │     │   └─ asyncio.gather([save_file(), save_file(), ...])
  │     ├─ Load PDFs concurrently
  │     │   └─ asyncio.gather([load_pdf(), load_pdf(), ...])
  │     └─ Return Document objects with metadata
  │
  ├─ [2] DocumentClassifier.classify()
  │     │
  │     ├─ Format documents into prompt
  │     ├─ Get cached LLM instance
  │     ├─ Call Gemini API (structured output)
  │     │   └─ Returns ClassificationResult
  │     └─ Return classification for all 5 types
  │
  ├─ [3] DocumentExtractor.extract_batch()
  │     │
  │     ├─ Filter documents where present=True
  │     ├─ Create extraction tasks
  │     ├─ Execute extractions in parallel
  │     │   └─ asyncio.gather([
  │     │         extract_single(doc1),
  │     │         extract_single(doc2),
  │     │         ...
  │     │       ])
  │     │
  │     │   Each extract_single():
  │     │   ├─ Find document pages
  │     │   ├─ Combine page content
  │     │   ├─ Format with prompt template
  │     │   ├─ Get cached extractor
  │     │   ├─ Call Gemini API (structured output)
  │     │   └─ Return ExtractionResult
  │     │
  │     └─ Return ExtractionResponse
  │
  └─ Return ClaimGenerationResponse
       └─ {classification: {...}, extraction: {...}}
```

## Component Interaction

### Layer Responsibilities

#### 1. **API Layer** (`app/api/`)
```
Responsibilities:
  • HTTP request/response handling
  • Input validation
  • Route definition
  • Dependency resolution
  • OpenAPI documentation

Dependencies:
  → Services, Agents (via dependency injection)
  → Schemas (for validation)
```

#### 2. **Service Layer** (`app/services/`)
```
Responsibilities:
  • Business logic
  • File operations
  • Data validation
  • External system interaction

Dependencies:
  → Core (config)
  → Exceptions
  → External libraries (LangChain loaders)
```

#### 3. **Agent Layer** (`app/agents/`)
```
Responsibilities:
  • LLM orchestration
  • Document classification
  • Data extraction
  • Prompt management

Dependencies:
  → Core (LLM, prompts)
  → Schemas (models)
  → Services (indirectly via API)
```

#### 4. **Core Layer** (`app/core/`)
```
Responsibilities:
  • LLM initialization and caching
  • Prompt templates
  • Configuration management
  • Shared utilities

Dependencies:
  → Config
  → External LLM APIs
```

#### 5. **Schema Layer** (`app/schemas/`)
```
Responsibilities:
  • Data models
  • Validation rules
  • Request/response structures
  • Type definitions

Dependencies:
  → None (pure Pydantic models)
```

## Data Flow

### Document Classification Flow

```
Documents
    │
    ├─ Extract metadata (filename, page numbers)
    │
    ├─ Format into classification prompt
    │   └─ "Source: doc_1.pdf, Page: 1\n[content]..."
    │
    ├─ Send to Gemini API via LangChain
    │   └─ with_structured_output(ClassificationResult)
    │
    ├─ Receive structured response
    │   {
    │     BILL: {present: true, confidence: 0.95, ...},
    │     DISCHARGE_SUMMARY: {present: false, ...},
    │     ...
    │   }
    │
    └─ Return ClassificationResult
```

### Document Extraction Flow

```
ClassificationResult + Documents
    │
    ├─ Filter: where present=True
    │   └─ [BILL, ID_CARD]
    │
    ├─ For each document type:
    │   │
    │   ├─ Find document by filename
    │   │
    │   ├─ Combine all pages
    │   │   └─ "Page 1:\n[content]\n---\nPage 2:\n[content]..."
    │   │
    │   ├─ Select extraction prompt template
    │   │   └─ EXTRACTION_PROMPTS[DocumentType.BILL]
    │   │
    │   ├─ Get/create cached extractor
    │   │   └─ llm.with_structured_output(BillExtraction)
    │   │
    │   ├─ Send to Gemini API
    │   │
    │   └─ Receive structured data
    │       {
    │         hospital_name: "City Hospital",
    │         patient_name: "John Doe",
    │         total_amount: 5000.0,
    │         ...
    │       }
    │
    ├─ Aggregate results
    │
    └─ Return ExtractionResponse
```

## Dependency Injection Pattern

```
┌────────────────────────┐
│   Endpoint Function    │
│                        │
│ async def endpoint(    │
│   loader: DocLoaderDep │ ◄─── Type annotation
│   classifier: ...      │
│   extractor: ...       │
│ ):                     │
└───────────┬────────────┘
            │
            │ FastAPI resolves dependencies
            │
            ▼
┌─────────────────────────────────────────┐
│         Dependency Providers            │
│                                         │
│ def get_document_loader():             │
│     return DocumentLoaderService()      │
│                                         │
│ def get_classifier():                  │
│     return DocumentClassifier()         │
│                                         │
│ def get_extractor():                   │
│     return DocumentExtractor()          │
└─────────────────────────────────────────┘
            │
            ├─ Each dependency can have its own dependencies
            │
            ▼
┌─────────────────────────────────────────┐
│         Service Instances               │
│                                         │
│ DocumentLoaderService()                │
│   └─ Uses: settings, logger            │
│                                         │
│ DocumentClassifier()                   │
│   └─ Uses: get_llm(), prompts          │
│                                         │
│ DocumentExtractor()                    │
│   └─ Uses: get_llm(), prompts          │
└─────────────────────────────────────────┘
```

## Performance Optimizations

### 1. LLM Instance Caching
```python
@lru_cache(maxsize=1)
def get_llm():
    return ChatGoogleGenerativeAI(...)

# First call: Creates instance
# Subsequent calls: Returns cached instance
```

### 2. Structured Output Caching
```python
class DocumentExtractor:
    def __init__(self):
        self._extractors = {}
    
    def _get_extractor(self, doc_type):
        if doc_type not in self._extractors:
            self._extractors[doc_type] = self.llm.with_structured_output(...)
        return self._extractors[doc_type]

# Avoids recreating structured output wrappers
```

### 3. Concurrent Processing
```python
# File saving
save_tasks = [save_file(f, i) for i, f in enumerate(files)]
saved_paths = await asyncio.gather(*save_tasks)

# Document loading
load_tasks = [load_document(path) for path in saved_paths]
documents = await asyncio.gather(*load_tasks)

# Data extraction
extract_tasks = [extract_single(doc) for doc in docs]
results = await asyncio.gather(*extract_tasks)
```

## Error Handling Strategy

```
Request
  │
  ├─ Input Validation
  │   └─ HTTPException (400) if invalid
  │
  ├─ File Validation
  │   └─ HTTPException (400) if size/type invalid
  │
  ├─ Document Processing
  │   └─ DocumentProcessingError (500) → Custom handler
  │
  ├─ Classification
  │   └─ ClassificationError (500) → Custom handler
  │
  ├─ Extraction
  │   └─ ExtractionError (500) → Custom handler
  │
  └─ Generic Exception
      └─ FastAPI default handler (500)
```

## Configuration Cascade

```
Environment Variables (.env)
    │
    ▼
Settings (pydantic-settings)
    │
    ├─ Validation
    ├─ Type conversion
    ├─ Default values
    │
    ▼
Application Components
    │
    ├─ Core (LLM initialization)
    ├─ Services (file paths, limits)
    ├─ API (CORS, versioning)
    └─ Logging (level, format)
```

## Scalability Considerations

### Current Architecture Supports:

1. **Horizontal Scaling**
   - Stateless services
   - No in-memory state sharing
   - Can run multiple instances behind load balancer

2. **Vertical Scaling**
   - Async I/O for better resource utilization
   - Concurrent processing
   - Efficient memory usage

3. **Future Enhancements**
   - Add Redis for caching LLM responses
   - Add database for document metadata
   - Add queue system for background processing
   - Add rate limiting
   - Add authentication/authorization

## Security Layers

```
Client Request
    │
    ├─ [1] CORS Middleware
    │      └─ Validates origin
    │
    ├─ [2] Input Validation
    │      └─ Pydantic models
    │
    ├─ [3] File Validation
    │      ├─ File type whitelist
    │      ├─ Size limits
    │      └─ Filename sanitization
    │
    ├─ [4] API Key Protection
    │      └─ Environment variables
    │
    └─ [5] Exception Handling
           └─ No sensitive data in responses
```

## Monitoring Points

```
Application Lifecycle
    │
    ├─ Startup
    │   └─ Log: "Application startup"
    │
    ├─ Request Received
    │   └─ Log: "Processing N files"
    │
    ├─ Document Loading
    │   └─ Log: "Loaded N pages from M files"
    │
    ├─ Classification
    │   └─ Log: "Classification complete"
    │
    ├─ Extraction
    │   └─ Log: "Extraction complete: X successful, Y failed"
    │
    ├─ Errors
    │   └─ Log: Detailed error with context
    │
    └─ Shutdown
        └─ Log: "Application shutdown"
```

This architecture provides a solid foundation that is maintainable, testable, scalable, and follows industry best practices for FastAPI applications.

