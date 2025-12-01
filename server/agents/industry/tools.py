# agents/industry/tools.py
from datetime import datetime, timedelta
from typing import List
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

class IndustrySearchInput(BaseModel):
    """Input schema for industry insights tool"""
    ticker: str = Field(..., description="Stock ticker symbol to analyze its industry/sector")

def search_recent_industry_insights(ticker: str) -> str:
    """
    Search for recent industry/sector trends, reports, and competitive analysis.
    """
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    
    query = f"{ticker} industry OR sector trends OR competition OR headwinds OR tailwinds OR market share 2025"
    
    try:
        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=10,
            time_range="month",
            include_domains=["bloomberg.com", "reuters.com", "wsj.com", "forbes.com", "mckinsey.com", "statista.com", "ft.com"],
            exclude_domains=["reddit.com", "twitter.com", "x.com"],
        )
        
        if not response.get("results"):
            return "No recent industry insights found."

        formatted = []
        for r in response["results"]:
            title = r.get("title", "No title")
            snippet = r.get("content", "")[:500]
            url = r.get("url", "")
            formatted.append(f"• {title}\n  {snippet}\n  Source: {url}")

        return "\n\n".join(formatted)
        
    except Exception as e:
        return f"Industry search failed: {str(e)}"

# Fixed: Use StructuredTool with schema
search_industry_tool = StructuredTool.from_function(
    func=search_recent_industry_insights,
    name="search_recent_industry_insights",
    description="Search for recent industry reports, sector trends, competitive dynamics, and analyst insights for a stock's sector. Input: ticker symbol.",
    args_schema=IndustrySearchInput,
)

# # agents/industry/tools.py
# from datetime import datetime, timedelta
# from typing import Optional
# from langchain_core.tools import Tool
# from tavily import TavilyClient
# import os
# from dotenv import load_dotenv

# load_dotenv()  # Load .env for TAVILY_API_KEY

# def search_recent_industry_insights(query: str, max_results: int = 10, include_domains: list = None, exclude_domains: list = None) -> str:
#     """
#     Searches for recent industry reports, analyses, and news using Tavily API.
#     Optimized for sector insights: trends, competition, dynamics from credible sources.
#     Returns JSON-like string with top results (title | snippet | url | date).
#     """
#     client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    
#     # 30-day cutoff
#     cutoff_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
#     # Tavily params (focus on credible, analytical sources)
#     response = client.search(
#         query=query,
#         search_depth="advanced",  # Deeper for reports/analyses
#         max_results=max_results,
#         time_range="month",  # Last 30 days
#         include_domains=include_domains or ["bloomberg.com", "reuters.com", "wsj.com", "forbes.com", "mckinsey.com", "deloitte.com", "statista.com"],  # Reports + outlets
#         exclude_domains=exclude_domains or ["reddit.com", "twitter.com", "facebook.com"],  # Avoid social noise
#         include_answer=False,  # Raw results for analysis
#     )
    
#     if not response.get("results"):
#         return "No recent industry insights found."
    
#     # Format for easy parsing (title | snippet | url | date)
#     formatted = []
#     for result in response["results"]:
#         date_str = result.get("date", "Unknown date")
#         formatted.append(f"{result['title']} | {result['content']} | {result['url']} | {date_str}")
    
#     return "\n".join(formatted)

# # LangChain Tool for Groq binding
# search_industry_tool = Tool(
#     name="search_recent_industry_insights",
#     description="Search for the top 10 most relevant recent industry reports, analyses, and news for a stock's sector from the last 30 days. Input: a query like 'AAPL industry sector analysis'. Focuses on credible sources (e.g., Bloomberg, McKinsey). Returns: formatted list of title | snippet | URL | date.",
#     func=search_recent_industry_insights,
# )