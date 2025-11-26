from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

class DocumentProcessingError(Exception):
    def __init__(self, detail: str, filename: str = None):
        self.detail = detail
        self.filename = filename

class ExtractionError(Exception):
    def __init__(self, detail: str):
        self.detail = detail

class ClassificationError(Exception):
    def __init__(self, detail: str):
        self.detail = detail

async def document_processing_error_handler(
    request: Request,
    exc: DocumentProcessingError
):
    logger.error(f"Document processing error: {exc.detail} (file: {exc.filename})")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "document_processing_failed",
            "detail": exc.detail,
            "filename": exc.filename
        }
    )

async def extraction_error_handler(request: Request, exc: ExtractionError):
    logger.error(f"Extraction error: {exc.detail}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "extraction_failed",
            "detail": exc.detail
        }
    )

async def classification_error_handler(request: Request, exc: ClassificationError):
    logger.error(f"Classification error: {exc.detail}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "classification_failed",
            "detail": exc.detail
        }
    )

def setup_exception_handlers(app):
    app.add_exception_handler(DocumentProcessingError, document_processing_error_handler)
    app.add_exception_handler(ExtractionError, extraction_error_handler)
    app.add_exception_handler(ClassificationError, classification_error_handler)

