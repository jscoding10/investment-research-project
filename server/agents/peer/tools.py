from datetime import datetime, timedelta
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

class PeerSearchInput(BaseModel):
    """Input schema for peer search tool"""
    ticker: str = Field(..., description="Stock ticker symbol (e.g., MSFT)")

def search_recent_peer_insights(ticker: str) -> str:
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    
    query = f"{ticker} vs competitors OR peers OR peer comparison OR earnings vs peers OR valuation vs peers OR market share shift"
    
    try:
        response = client.search(
            query=query,
            search_depth="advanced",
            topic="news",
            max_results=10,
            time_range="month",  # ← 30 days
            include_domains=[
                "cnbc.com", "bloomberg.com", "reuters.com", "wsj.com",
                "finance.yahoo.com", "seekingalpha.com", "morningstar.com", "barrons.com"
            ],
            exclude_domains=["reddit.com", "twitter.com", "x.com", "medium.com"],
        )
        
        results = response.get("results", [])
        if not results:
            return "No recent peer comparison articles found in the last 30 days."

        formatted = []
        for r in results:
            title = r.get("title", "No title")
            snippet = r.get("content", "")[:450]
            url = r.get("url", "")
            date = r.get("published_date", r.get("date", "Recent"))
            formatted.append(f"• {title}\n  {snippet}\n  Source: {url} | {date}")

        return "\n\n".join(formatted)
        
    except Exception as e:
        return f"Peer search failed: {str(e)}"

# Clean, short name — just like your industry tool
search_peer_tool = StructuredTool.from_function(
    func=search_recent_peer_insights,
    name="search_recent_peer_insights",
    description="Search for recent articles comparing a stock ticker to its direct competitors (performance, valuation, earnings, market share) from the last 30 days.",
    args_schema=PeerSearchInput,
)