import dotenv
from datetime import datetime, timedelta
from langchain_groq import ChatGroq  

from agents.shared.agent_utils import run_agent_with_tools  
from agents.shared.llm_models import LLM_MODELS
from agents.industry.prompt import industry_research_prompt
from agents.industry.tools import search_industry_tool  

dotenv.load_dotenv()

def get_industry_sentiment(ticker: str, industry: str) -> str:
    """
    Get industry sentiment using Groq + Tavily search tool.
    Analyzes sector trends, competition, and tailwinds/headwinds from recent reports.
    """

    current_date = datetime.now().strftime("%Y-%m-%d")
    cutoff_date = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")

    prompt = industry_research_prompt.format(
        ticker=ticker,
        industry=industry,
        current_date=current_date,
        cutoff_date=cutoff_date,
    )
    
    # Groq model from shared config
    model = LLM_MODELS["groq-llama"]  # "llama-3.3-70b-versatile"
    
    llm = ChatGroq(
        model=model,
        temperature=0.0,  # Deterministic for analysis
    )
    
    # Run with tool (Groq auto-calls Tavily)
    tools = [search_industry_tool]
    result = run_agent_with_tools(llm=llm, prompt=prompt, tools=tools)
    
    return result