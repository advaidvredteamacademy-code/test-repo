from typing import Annotated
from fastapi import Depends

from app.services.document_loader import DocumentLoaderService
from app.agents.classification import DocumentClassifier
from app.agents.extraction import DocumentExtractor

def get_document_loader() -> DocumentLoaderService:
    return DocumentLoaderService()

def get_classifier() -> DocumentClassifier:
    return DocumentClassifier()

def get_extractor() -> DocumentExtractor:
    return DocumentExtractor()

DocumentLoaderDep = Annotated[DocumentLoaderService, Depends(get_document_loader)]
ClassifierDep = Annotated[DocumentClassifier, Depends(get_classifier)]
ExtractorDep = Annotated[DocumentExtractor, Depends(get_extractor)]

