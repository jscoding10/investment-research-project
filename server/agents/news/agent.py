import dotenv
from datetime import datetime, timedelta
from logger import get_logger

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage  

from agents.shared.llm_models import LLM_MODELS
from agents.news.prompt import news_research_prompt

dotenv.load_dotenv()

logger = get_logger(__name__)


def get_news_sentiment(ticker: str, business: str):
    """
    Retrieves structured news sentiment for the ticker and business (BULLISH/BEARISH/NEUTRAL) 
    using live web search grounded in the most recent 30 days of data.
    """
    try:
        current_date = datetime.now().strftime("%Y-%m-%d")
        cutoff_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        prompt = news_research_prompt.format(
            ticker=ticker,
            business=business,
            current_date=current_date,
            cutoff_date=cutoff_date,
        )
        
        model = LLM_MODELS['groq-compound-mini']

        llm = ChatGroq(
            model=model,
            temperature=0.0,
            max_tokens=600,               
        )
    
        result = llm.invoke([HumanMessage(content=prompt)])
        
        return result.content.strip()
    except Exception as e:
        logger.error(f"Error in get_news_sentiment: {e}", exc_info=True)
        return f"Error executing agent: {str(e)}"