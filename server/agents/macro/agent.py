import dotenv
from langchain_groq import ChatGroq

from agents.macro.prompt import macro_research_prompt
from agents.macro.tools import get_macro_data_tool
from agents.shared.agent_utils import run_agent_with_tools
from agents.shared.llm_models import LLM_MODELS
from models.agent import MacroSentimentOutput

dotenv.load_dotenv()

def get_macro_sentiment() -> str:
    """
    Returns bullish/bearish/neutral view on equities based on latest FRED macro data.
    """
    prompt = macro_research_prompt
    tools = [get_macro_data_tool]

    model_name = LLM_MODELS["groq-llama"] 

    llm = ChatGroq(
        model=model_name,
        temperature=0.0,           
    )

    result = run_agent_with_tools(llm, prompt, tools, MacroSentimentOutput)
    return result