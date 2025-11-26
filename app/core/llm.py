from functools import lru_cache
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import settings

@lru_cache(maxsize=1)
def get_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=settings.LLM_MODEL,
        api_key=settings.GOOGLE_API_KEY,
        temperature=settings.LLM_TEMPERATURE,
        max_retries=settings.LLM_MAX_RETRIES,
    )

@lru_cache(maxsize=1)
def get_llm_with_thinking() -> ChatGoogleGenerativeAI:
    """Get LLM configured with thinking/extended thinking capability"""
    return ChatGoogleGenerativeAI(
        model=settings.LLM_MODEL,
        api_key=settings.GOOGLE_API_KEY,
        temperature=settings.LLM_TEMPERATURE,
        max_retries=settings.LLM_MAX_RETRIES,
        enable_thinking=True,  # Enable thinking for Gemini models
    )

