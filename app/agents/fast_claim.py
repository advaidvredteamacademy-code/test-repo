from langchain_core.documents import Document
from typing import List
import asyncio
import logging

from app.schemas.fast_claim import FastClaimResponse, ClassificationAndExtraction
from app.core.prompts import UNIFIED_FAST_CLAIM_PROMPT
from app.core.llm import get_llm_with_thinking

logger = logging.getLogger(__name__)

class FastClaimGenerator:
    """
    Fast claim generator that performs both classification and extraction 
    in a single LLM request with thinking enabled.
    """
    
    def __init__(self):
        self.llm = get_llm_with_thinking()
        self.structured_llm = self.llm.with_structured_output(
            ClassificationAndExtraction,
            include_raw=True  # Include raw response to capture thinking
        )
    
    async def generate_claim(self, documents: List[Document]) -> FastClaimResponse:
        """
        Generate complete claim with classification and extraction in a single request.
        
        Args:
            documents: List of loaded documents
            
        Returns:
            FastClaimResponse with combined results and thinking process
        """
        logger.info(f"starting fast claim generation with {len(documents)} document pages")
        # Combine all documents into a single text
        documents_text = "\n\n".join([
            f"=== Document: {doc.metadata.get('source', 'Unknown')}, Page: {doc.metadata.get('page', 'Unknown')} ===\n{doc.page_content}"
            for doc in documents
        ])
        
        # Format the unified prompt
        prompt = UNIFIED_FAST_CLAIM_PROMPT.format(documents_text=documents_text)
        
        # Run the LLM in executor to avoid blocking
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            self.structured_llm.invoke,
            prompt
        )
        
        # Extract the structured result and thinking
        parsed_result = response.get("parsed")
        raw_response = response.get("raw")
        
        # Extract thinking from raw response if available
        thinking_text = None
        if hasattr(raw_response, 'usage_metadata'):
            # Try to get thinking from usage metadata or response metadata
            thinking_text = getattr(raw_response, 'thinking', None)
        
        # If thinking is in the content, try to extract it
        if not thinking_text and hasattr(raw_response, 'content'):
            content = raw_response.content
            if isinstance(content, list):
                for block in content:
                    if hasattr(block, 'type') and block.type == 'thinking':
                        thinking_text = block.text
                        break
            elif isinstance(content, str):
                thinking_text = content
        
        logger.info("fast claim generation complete")
        return FastClaimResponse(
            result=parsed_result,
            thinking=thinking_text
        )

