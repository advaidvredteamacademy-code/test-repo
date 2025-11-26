from typing import List, Dict
import asyncio
import logging
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
from app.exceptions import ExtractionError

logger = logging.getLogger(__name__)

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
            logger.info(f"Starting extraction for {filename} (type: {document_type.value})")
            
            doc_pages = [
                doc for doc in documents 
                if doc.metadata.get('source') == filename
            ]
            
            if not doc_pages:
                logger.warning(f"No pages found for {filename}")
                return ExtractionResult(
                    filename=filename,
                    document_type=document_type.value,
                    extraction_status="failed",
                    extracted_data=None,
                    error_message=f"Document {filename} not found in loaded documents"
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
            
            logger.info(f"Successfully extracted data from {filename}")
            
            return ExtractionResult(
                filename=filename,
                document_type=document_type.value,
                extraction_status="success",
                extracted_data=result.model_dump(),
                error_message=None
            )
            
        except Exception as e:
            logger.error(f"Error extracting data from {filename}: {str(e)}")
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
        try:
            logger.info("Starting parallel document extraction")
            
            tasks = []
            for doc_type in DocumentType:
                doc_info = getattr(classification_result, doc_type.value)
                
                if doc_info.present:
                    logger.info(f"Queuing extraction for {doc_info.document_file_name} (type: {doc_type.value})")
                    task = self.extract_single(
                        filename=doc_info.document_file_name,
                        document_type=doc_type,
                        documents=documents
                    )
                    tasks.append(task)
            
            if not tasks:
                logger.warning("No documents marked as present for extraction")
                return ExtractionResponse(
                    results=[],
                    total_extracted=0,
                    successful_extractions=0,
                    failed_extractions=0
                )
            
            logger.info(f"Executing {len(tasks)} extraction tasks in parallel")
            results = await asyncio.gather(*tasks)
            
            successful = sum(1 for r in results if r.extraction_status == "success")
            failed = sum(1 for r in results if r.extraction_status == "failed")
            
            logger.info(f"Extraction complete: {successful} successful, {failed} failed")
            
            return ExtractionResponse(
                results=results,
                total_extracted=len(results),
                successful_extractions=successful,
                failed_extractions=failed
            )
            
        except Exception as e:
            logger.error(f"Batch extraction failed: {str(e)}")
            raise ExtractionError(detail=f"Failed to extract documents: {str(e)}")

