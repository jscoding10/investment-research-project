import dotenv
from langchain_groq import ChatGroq

from agents.shared.agent_utils import run_agent_with_tools
from agents.shared.llm_models import LLM_MODELS
from agents.fundamentals.prompt import fundamentals_research_prompt
from agents.fundamentals.tools import get_fundamentals_tool

dotenv.load_dotenv()


def get_fundamental_sentiment(ticker: str) -> str:
    """
    Returns [UNDERVALUED / OVERVALUED / FAIRLY VALUED] based on real fundamental data
    from Yahoo Finance (via yfinance) — analyzed by Groq Llama 3.3 70B.
    """
    prompt = f"{fundamentals_research_prompt}\n\nAnalyze the business fundamentals for ticker: {ticker}"
    tools = [get_fundamentals_tool]

    model_name = LLM_MODELS['groq-llama']

    llm = ChatGroq(
        model=model_name,
        temperature=0.0,       
    )

    result = run_agent_with_tools(llm=llm, prompt=prompt, tools=tools)
    return result