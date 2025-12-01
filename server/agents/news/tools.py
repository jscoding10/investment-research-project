from datetime import datetime, timedelta
from typing import Optional, List
from langchain_core.tools import Tool, StructuredTool
from pydantic import BaseModel, Field
from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

class NewsSearchInput(BaseModel):
    """Input schema for news search tool"""
    ticker: str = Field(..., description="Stock ticker symbol (e.g., NVDA, AAPL)")

def search_recent_news(ticker: str) -> str:
    """
    Searches for recent news using Tavily API.
    Returns formatted string with top headlines, snippets, URLs, and dates.
    """
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    
    query = f"{ticker} stock news OR earnings OR guidance OR analyst OR upgrade OR downgrade"
    
    try:
        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=10,
            time_range="month",
            include_domains=["cnbc.com", "bloomberg.com", "reuters.com", "wsj.com", "finance.yahoo.com"],
            exclude_domains=["reddit.com", "twitter.com", "x.com"],
        )
        
        if not response.get("results"):
            return "No recent news found."

        formatted = []
        for r in response["results"]:
            title = r.get("title", "No title")
            snippet = r.get("content", "")[:400]
            url = r.get("url", "")
            date = r.get("date", "Recent")
            formatted.append(f"• {title}\n  {snippet}\n  Source: {url} | {date}")

        return "\n\n".join(formatted)
        
    except Exception as e:
        return f"News search failed: {str(e)}"

# Fixed: Use StructuredTool with proper schema
search_news_tool = StructuredTool.from_function(
    func=search_recent_news,
    name="search_recent_stock_news",
    description="Search for the top 10 most recent and credible news articles about a stock ticker from the last 30 days. Returns formatted list of headlines, snippets, and sources.",
    args_schema=NewsSearchInput,
)

# # agents/news/tools.py
# from datetime import datetime, timedelta
# from typing import Optional
# from langchain_core.tools import Tool
# from tavily import TavilyClient
# import os
# from dotenv import load_dotenv

# load_dotenv()  # Load .env for TAVILY_API_KEY

# def search_recent_news(query: str, max_results: int = 10, include_domains: list = None, exclude_domains: list = None) -> str:
#     """
#     Searches for recent news using Tavily API.
#     Returns JSON-like string with top headlines, snippets, URLs, and dates.
#     """
#     client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    
#     # Calculate 30-day cutoff
#     cutoff_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
#     # Tavily search params (optimized for news: recent, credible sources)
#     response = client.search(
#         query=query,
#         search_depth="advanced",  # Deeper crawl for better news coverage
#         max_results=max_results,
#         time_range="month",  # Last 30 days (matches your prompt)
#         include_domains=include_domains or ["cnbc.com", "bloomberg.com", "reuters.com", "wsj.com", "yahoo.com/finance"],  # Major outlets
#         exclude_domains=exclude_domains or ["reddit.com", "twitter.com"],  # Avoid noise
#         include_answer=False,  # We want raw results, not summarized
#     )
    
#     # Format results as easy-to-parse string (title | snippet | url | date)
#     if not response.get("results"):
#         return "No recent news found."
    
#     formatted = []
#     for result in response["results"]:
#         date_str = result.get("date", "Unknown date")
#         formatted.append(f"{result['title']} | {result['content']} | {result['url']} | {date_str}")
    
#     return "\n".join(formatted)

# # Create the LangChain Tool (for binding to Groq)
# search_news_tool = Tool(
#     name="search_recent_stock_news",
#     description="Search for the top 10 most recent news headlines and articles about a stock ticker from the last 30 days. Input: the stock ticker (e.g., 'AAPL'). Focuses on major outlets like CNBC, Bloomberg. Returns: formatted list of title | snippet | URL | date.",
#     func=search_recent_news,
# )