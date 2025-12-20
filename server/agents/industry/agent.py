import os
import dotenv
from datetime import datetime, timedelta
from logger import get_logger

from agents.shared.llm_models import LLM_MODELS
from agents.industry.prompt import industry_research_prompt

from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq  

dotenv.load_dotenv()

logger = get_logger(__name__)

def get_industry_sentiment(ticker: str, industry: str) -> str:
    """
    Retrieves structured industry sentiment for the ticker and industry (BULLISH/BEARISH/NEUTRAL)
    using live web search grounded in the most recent 60 days of data.
    Analyzes sector trends, competition, and tailwinds/headwinds from recent reports.
    """
    try:
        current_date = datetime.now().strftime("%Y-%m-%d")
        cutoff_date = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")

        prompt = industry_research_prompt.format(
            ticker=ticker,
            industry=industry,
            current_date=current_date,
            cutoff_date=cutoff_date,
        )
        
        model = LLM_MODELS['groq-compound-mini']

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found! "
                "Make sure you have a .env file with GROQ_API_KEY=your_real_key_here"
            )

        llm = ChatGroq(
            model=model,
            temperature=0.0,
            max_tokens=600,  
            groq_api_key = api_key              
        )
        
        result = llm.invoke([HumanMessage(content=prompt)])
        
        return result.content.strip()
    
    except Exception as e:
        logger.error(f"Error in get_industry_sentiment: {e}", exc_info=True)
        return f"Error executing agent: {str(e)}"