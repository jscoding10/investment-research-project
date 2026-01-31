import os
import dotenv

from agents.shared.crypto.agent_utils_crypto import run_agent_with_tools
from agents.shared.crypto.llm_models_crypto import LLM_MODELS, get_groq_llm
from agents.crypto.technical.prompt_crypto import technical_research_prompt
from agents.crypto.technical.tools_crypto import get_technical_analysis_tool
from models.crypto.agent_crypto import TechnicalSentimentOutput

dotenv.load_dotenv()

"""
Main function: analyzes any crypto ticker (like "BTC-USD" or "ETH-USD")
and returns a clean bullish/bearish/neutral summary using Groq.
"""
def get_technical_sentiment(ticker: str):
    prompt = f"{technical_research_prompt}\n\nAnalyze the technical indicators for ticker: {ticker}"
    tools = [get_technical_analysis_tool]
    model = LLM_MODELS["groq-llama"]
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found! "
            "Make sure you have a .env file with GROQ_API_KEY=your_real_key_here"
        )
    
    llm = get_groq_llm(model = model, api_key = api_key, temperature = 0.0)
   
    result = run_agent_with_tools(llm, prompt, tools, TechnicalSentimentOutput)
    return result