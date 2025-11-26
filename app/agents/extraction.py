from typing import List, Dict
import asyncio
from langchain_core.documents import Document

from app.schemas.document import DocumentType
from app.schemas.classification import ClassificationResult
from app.schemas.extraction import (
    ExtractionResult,
    ExtractionResponse,
    BillExtraction,
    DischargeSummaryExtraction,
    IDCardExtraction,
    PharmacyBillExtraction,
    ClaimFormExtraction
)
from app.core.llm import get_llm
from app.core.prompts import EXTRACTION_PROMPTS

EXTRACTION_MODELS = {
    DocumentType.BILL: BillExtraction,
    DocumentType.DISCHARGE_SUMMARY: DischargeSummaryExtraction,
    DocumentType.ID_CARD: IDCardExtraction,
    DocumentType.PHARMACY_BILL: PharmacyBillExtraction,
    DocumentType.CLAIM_FORM: ClaimFormExtraction,
}

class DocumentExtractor:
    def __init__(self):
        self.llm = get_llm()
        self._extractors: Dict = {}
    
    def _get_extractor(self, doc_type: DocumentType):
        if doc_type not in self._extractors:
            model_class = EXTRACTION_MODELS[doc_type]
            self._extractors[doc_type] = self.llm.with_structured_output(model_class)
        return self._extractors[doc_type]
    
    async def extract_single(
        self,
        filename: str,
        document_type: DocumentType,
        documents: List[Document]
    ) -> ExtractionResult:
        try:
            doc_pages = [
                doc for doc in documents 
                if doc.metadata.get('source') == filename
            ]
            
            if not doc_pages:
                return ExtractionResult(
                    filename=filename,
                    document_type=document_type.value,
                    extraction_status="failed",
                    extracted_data=None,
                    error_message=f"Document {filename} not found"
                )
            
            content = "\n\n--- Page Break ---\n\n".join([
                f"Page {doc.metadata.get('page', 'Unknown')}:\n{doc.page_content}"
                for doc in doc_pages
            ])
            
            prompt_template = EXTRACTION_PROMPTS[document_type]
            prompt = prompt_template.format(content=content)
            
            extractor = self._get_extractor(document_type)
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, extractor.invoke, prompt)
            
            return ExtractionResult(
                filename=filename,
                document_type=document_type.value,
                extraction_status="success",
                extracted_data=result.model_dump(),
                error_message=None
            )
            
        except Exception as e:
            return ExtractionResult(
                filename=filename,
                document_type=document_type.value,
                extraction_status="failed",
                extracted_data=None,
                error_message=str(e)
            )
    
    async def extract_batch(
        self,
        classification_result: ClassificationResult,
        documents: List[Document]
    ) -> ExtractionResponse:
        tasks = []
        for doc_type in DocumentType:
            doc_info = getattr(classification_result, doc_type.value)
            
            if doc_info.present:
                task = self.extract_single(
                    filename=doc_info.document_file_name,
                    document_type=doc_type,
                    documents=documents
                )
                tasks.append(task)
        
        if not tasks:
            return ExtractionResponse(
                results=[],
                total_extracted=0,
            )
        
        results = await asyncio.gather(*tasks)
        
        
        return ExtractionResponse(
            results=results,
            total_extracted=len(results),
        )

