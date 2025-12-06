import dotenv
from datetime import datetime, timedelta
from langchain_groq import ChatGroq

from agents.shared.agent_utils import run_agent_with_tools  
from agents.shared.llm_models import LLM_MODELS
from agents.peer.prompt import peer_research_prompt
from agents.peer.tools import search_peer_tool

dotenv.load_dotenv()

def get_peer_sentiment(ticker: str) -> str:
    """
    Get peer-relative sentiment using only ticker (30-day window).
    Matches industry agent structure exactly.
    """
    current_date = datetime.now().strftime("%Y-%m-%d")
    cutoff_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    prompt = peer_research_prompt.format(
        ticker=ticker,
        current_date=current_date,
        cutoff_date=cutoff_date,
    )

    model = LLM_MODELS["groq-llama"]  # or switch to llama-3.1-70b-versatile if throttled

    llm = ChatGroq(model=model, temperature=0.0)

    tools = [search_peer_tool]
    result = run_agent_with_tools(llm=llm, prompt=prompt, tools=tools)

    # Fallback — same style as industry
    if not result or result.strip() == "" or "error" in result.lower():
        return "[NEUTRAL]\nLimited peer comparison data in last 30 days — stock likely tracking peers.\nConfidence: Low"

    return result