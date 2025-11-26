from langchain_core.documents import Document
from typing import List
import asyncio
import logging

from app.schemas.classification import ClassificationResult
from app.core.prompts import CLASSIFICATION_PROMPT
from app.core.llm import get_llm
from app.exceptions import ClassificationError

logger = logging.getLogger(__name__)

class DocumentClassifier:
    def __init__(self):
        self.llm = get_llm()
        self.structured_llm = self.llm.with_structured_output(ClassificationResult)
    
    async def classify(self, documents: List[Document]) -> ClassificationResult:
        try:
            logger.info(f"Starting classification for {len(documents)} document pages")
            
            documents_text = "\n\n".join([
                f"Source: {doc.metadata.get('source', 'Unknown')}, Page: {doc.metadata.get('page', 'Unknown')}\n{doc.page_content}"
                for doc in documents
            ])
            
            prompt = CLASSIFICATION_PROMPT.format(documents_text=documents_text)
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.structured_llm.invoke,
                prompt
            )
            
            logger.info("Classification completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Classification failed: {str(e)}")
            raise ClassificationError(detail=f"Failed to classify documents: {str(e)}")

