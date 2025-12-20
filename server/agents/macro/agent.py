import os
import dotenv
from logger import get_logger

from agents.macro.prompt import macro_research_prompt
from agents.macro.tools import get_macro_data_tool
from agents.shared.agent_utils import run_agent_with_tools
from agents.shared.llm_models import LLM_MODELS, get_groq_llm
from models.agent import MacroSentimentOutput

dotenv.load_dotenv()

logger = get_logger(__name__)

def get_macro_sentiment() -> str:
    """
    Returns bullish/bearish/neutral view on equities based on latest FRED macro data.
    """
    try:
        prompt = macro_research_prompt
        tools = [get_macro_data_tool]

        model = LLM_MODELS["groq-llama"] 

        api_key = os.getenv("GROQ_API_KEY_2")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found! "
                "Make sure you have a .env file with GROQ_API_KEY_2=your_real_key_here"
            )   


        llm = get_groq_llm(model = model, api_key = api_key, temperature = 0.0)

        result = run_agent_with_tools(llm, prompt, tools, MacroSentimentOutput)
        return result
    except Exception as e:
        logger.error(f"Error in get_macro_sentiment: {e}", exec_info = True)
        return f"Error executing agent: {str(e)}"