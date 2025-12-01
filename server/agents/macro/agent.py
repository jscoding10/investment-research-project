import dotenv
from langchain_groq import ChatGroq

from agents.macro.prompt import macro_research_prompt
from agents.macro.tools import get_macro_data_tool
from agents.shared.agent_utils import run_agent_with_tools
from agents.shared.llm_models import LLM_MODELS

dotenv.load_dotenv()


def get_macro_sentiment() -> str:
    """
    Returns bullish/bearish/neutral view on equities based on latest FRED macro data.
    Uses Groq Groq (Llama 3.3 70B) + FRED tool.
    """
    prompt = macro_research_prompt
    tools = [get_macro_data_tool]

    # Use your fast Groq model
    model_name = LLM_MODELS["groq-llama"]  # "llama-3.3-70b-versatile"

    llm = ChatGroq(
        model=model_name,
        temperature=0.0,           
        # api_key automatically loaded from .env → GROQ_API_KEY
    )

    result = run_agent_with_tools(llm=llm, prompt=prompt, tools=tools)
    return result