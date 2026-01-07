import os
import dotenv
from datetime import datetime, timedelta
from util.logger import get_logger

from langchain_core.messages import HumanMessage

from agents.shared.llm_models import LLM_MODELS, get_groq_compound_llm
from agents.peer.prompt import peer_research_prompt

logger = get_logger(__name__)

dotenv.load_dotenv()

def get_peer_sentiment(ticker: str, business: str) -> str:
    """
    Retrieves structured peer-relative sentiment (POSITIVE/NEUTRAL/NEGATIVE) for the given ticker
    using live web search grounded in the most recent 20 days of data.
    """
    try:
        current_date = datetime.now().strftime("%Y-%m-%d")
        cutoff_date = (datetime.now() - timedelta(days=20)).strftime("%Y-%m-%d")

        prompt = peer_research_prompt.format(
            ticker=ticker,
            business=business,
            current_date=current_date,
            cutoff_date=cutoff_date,
        )

        model = LLM_MODELS['groq-compound-mini']

        api_key = os.getenv("GROQ_API_KEY_3")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found! "
                "Make sure you have a .env file with GROQ_API_KEY_3=your_real_key_here"
            )   

        llm = get_groq_compound_llm(model = model, api_key = api_key, max_tokens = 600, temperature = 0.0)

        result = llm.invoke([HumanMessage(content=prompt)])

        return result.content.strip()

    except Exception as e:
        logger.error(f"Error in get_peer_sentiment: {e}", exc_info=True)
        return f"Error executing agent: {str(e)}"