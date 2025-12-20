
import os
from typing import Any, Dict, Optional

import dotenv
from langchain_groq import ChatGroq

from agents.shared.agent_utils import run_agent_with_tools
from agents.shared.llm_models import LLM_MODELS
from agents.fundamentals.prompt import fundamentals_research_prompt
from agents.fundamentals.tools import (
    get_fundamentals_tool,
    get_earnings_and_financial_health,
)

from models.agent import FundamentalSentimentOutput

dotenv.load_dotenv()


def get_fundamental_sentiment(
    ticker: str, cached_info: Optional[Dict[str, Any]] = None
):
    """
    Generate fundamental sentiment analysis for a ticker.

    Args:
        ticker: Stock ticker symbol
        cached_info: Optional pre-fetched yfinance ticker.info to avoid duplicate API calls
    """
    model_name = LLM_MODELS['groq-llama']

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found! "
            "Make sure you have a .env file with GROQ_API_KEY=your_real_key_here"
        )

    llm = ChatGroq(
        model= model_name,
        temperature= 0.0,
        groq_api_key = api_key       
    )

    if cached_info is not None:
        # Use cached info - call function directly instead of via tool
        fundamentals_data = get_earnings_and_financial_health(
            ticker=ticker, cached_info=cached_info
        )
        # Inject the data directly into the prompt for analysis
        prompt = f"{fundamentals_research_prompt}\n\n"
        prompt += f"Analyze the business fundamentals for ticker: {ticker}\n\n"
        prompt += f"Here is the fundamental data:\n{fundamentals_data.model_dump_json(indent=2)}"
        structured_llm = llm.with_structured_output(FundamentalSentimentOutput)
        result = structured_llm.invoke(prompt)
        return result
    else:
        # No cached info - use tool-calling approach
        prompt = f"{fundamentals_research_prompt}\n\nAnalyze the business fundamentals for ticker: {ticker}"
        tools = [get_fundamentals_tool]
        result = run_agent_with_tools(llm, prompt, tools, FundamentalSentimentOutput)
        return result