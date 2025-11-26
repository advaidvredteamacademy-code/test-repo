from langchain_core.documents import Document
from typing import List
import asyncio

from app.schemas.classification import ClassificationResult
from app.core.prompts import CLASSIFICATION_PROMPT
from app.core.llm import get_llm

class DocumentClassifier:
    def __init__(self):
        self.llm = get_llm()
        self.structured_llm = self.llm.with_structured_output(ClassificationResult)
    
    async def classify(self, documents: List[Document]) -> ClassificationResult:
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
        
        return result

