from functools import lru_cache
from langchain_groq import ChatGroq

LLM_MODELS = {
    "groq-llama": "llama-3.3-70b-versatile",
    "groq-compound": "groq/compound",
    "groq-compound-mini": "groq/compound-mini"
}

@lru_cache(maxsize = 10)
def get_groq_llm(model: str, api_key: str, temperature: float = 0.0) -> ChatGroq:
    """
    Get a cached Groq instance.

    Args:
        model: The Groq model name
        groq_api_key: The Groq project api key
        temperature: The temperature setting (default 0.0)

    Returns:
        Cached Groq instance
    """
    return ChatGroq(model = model, temperature = temperature, groq_api_key = api_key)

@lru_cache(maxsize = 10)
def get_groq_compound_llm(model: str, api_key: str, max_tokens: int, temperature: float = 0.0) -> ChatGroq:
    """
    Get a cached Groq Compound instance.

    Args:
        model: The Groq model name
        groq_api_key: The Groq project api key
        temperature: The temperature setting (default 0.0)

    Returns:
        Cached Groq instance
    """
    return ChatGroq(model = model, temperature = temperature, max_tokens = max_tokens, groq_api_key = api_key)