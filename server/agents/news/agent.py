import dotenv
from datetime import datetime, timedelta
from langchain_groq import ChatGroq

from agents.shared.agent_utils import run_agent_with_tools  
from agents.shared.llm_models import LLM_MODELS
from agents.news.prompt import news_research_prompt
from agents.news.tools import search_news_tool


dotenv.load_dotenv()


def get_news_sentiment(ticker: str):
    """
    Get news sentiment using Groq + Tavily search tool.
    Groq analyzes the fetched news for bullish/bearish/neutral.
    """

    current_date = datetime.now().strftime("%Y-%m-%d")
    cutoff_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    prompt = news_research_prompt.format(
        ticker=ticker,
        current_date=current_date,
        cutoff_date=cutoff_date,
    )
    model = LLM_MODELS["groq-llama"]

    llm = ChatGroq(
        model=model,
        temperature=0.0,  # Low randomness for consistent analysis
        # api_key automatically loaded from .env → GROQ_API_KEY
    )

    # Run with the search tool (Groq will call it automatically if needed)
    tools = [search_news_tool]
    result = run_agent_with_tools(llm=llm, prompt=prompt, tools=tools)

    return result