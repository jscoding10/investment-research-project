import os
import dotenv
from util.logger import get_logger

from agents.crypto.macro.prompt_crypto import macro_research_prompt
from agents.crypto.macro.tools_crypto import get_macro_data_tool
from agents.shared.crypto.agent_utils_crypto import run_agent_with_tools
from agents.shared.crypto.llm_models_crypto import LLM_MODELS, get_groq_llm
from models.crypto.agent_crypto import MacroSentimentOutput

dotenv.load_dotenv()

logger = get_logger(__name__)

def get_macro_sentiment() -> str:
    """
    Returns bullish/bearish/neutral view on crypto based on latest FRED macro data.
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