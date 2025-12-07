# from datetime import datetime, timedelta
# from typing import Optional, List
# from langchain_core.tools import Tool, StructuredTool
# from pydantic import BaseModel, Field
# from tavily import TavilyClient
# import os
# from dotenv import load_dotenv

# load_dotenv()

# class NewsSearchInput(BaseModel):
#     """Input schema for news search tool"""
#     ticker: str = Field(..., description="Stock Ticker (e.g., AAPL)")
#     business: str = Field(..., description="Business/Company Name (e.g., Apple Inc.)")

# def search_recent_news(ticker: str, business: str) -> str:
#    """
#     Searches for recent news using Tavily API.
#     Returns formatted string with top headlines, snippets, URLs, and dates.
#     """
#    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    
#    query = f"{business} OR {ticker} stock news OR earnings OR guidance OR analyst OR upgrade OR downgrade"
    
#    try:
#         response = client.search(
#             query=query,
#             search_depth="advanced",
#             topic="news",  # Enables real-time news focus with published_date metadata
#             max_results=10,
#             time_range="month",
#             include_domains=["cnbc.com", "bloomberg.com", "reuters.com", "wsj.com", "finance.yahoo.com"],
#             exclude_domains=["reddit.com", "twitter.com", "x.com"],
#         )
        
#         if not response.get("results"):
#             return "No recent news found. Consider this as potentially neutral sentiment due to low activity."

#         formatted = []
#         for r in response["results"]:
#             title = r.get("title", "No title")
#             snippet = r.get("content", "")[:400]
#             url = r.get("url", "")
#             date = r.get("published_date", "Recent")  # Use published_date if available via topic="news"
#             formatted.append(f"• {title}\n  {snippet}\n  Source: {url} | {date}")

#         return "\n\n".join(formatted)
        
#    except Exception as e:
#         return f"News search failed: {str(e)}. Retry with broader query if needed."

# search_news_tool = StructuredTool.from_function(
#     func=search_recent_news,
#     name="search_recent_stock_news",
#     description="Search for the top 10 most recent and credible news articles about a business or stock (using both name and ticker) from the last 30 days. Returns formatted list of headlines, snippets, and sources.",
#     args_schema=NewsSearchInput,
# )

# agents/news/tools.py
from datetime import datetime, timedelta
from typing import List
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

class NewsSearchInput(BaseModel):
    """Input schema for news search tool"""
    ticker: str = Field(..., description="Stock Ticker (e.g., AAPL)")
    business: str = Field(..., description="Business/Company Name (e.g., Apple Inc.)")


def search_recent_stock_news(ticker: str, business: str) -> str:
    """
    Runs multiple targeted searches for high-quality, recent stock-specific news.
    Returns deduplicated results with inline citations that the LLM cannot drop.
    """
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    queries = [
        # f"{business} OR {ticker} stock news",
        # f"{business} OR {ticker} earnings OR guidance OR results",
        # f"{business} stock news",
        # f"{business} business",
        # f'"{business}" OR {ticker} "analyst rating" OR upgrade OR downgrade OR "price target"',
        # f'"{business}" "stock news"',
        # f'"{business}" business news',

        f'"{business}" OR {ticker} "analyst rating" OR upgrade OR downgrade OR "price target"',
        f'"{business}" "stock news"',
        f'"{business}" business news',
        f'"{business}" OR {ticker} earnings miss OR guidance cut OR lawsuit OR decline OR warning',  

    ]

    all_results: List[str] = []

    for query in queries:
        try:
            response = client.search(
                query=query,
                search_depth="advanced",
                topic="news",
                max_results=14,
                time_range="month",
                include_domains=[
                    "cnbc.com", "bloomberg.com", "reuters.com", "wsj.com",
                    "finance.yahoo.com", "marketwatch.com", "investing.com"
                ],
                exclude_domains=["reddit.com", "twitter.com", "x.com"],
            )

            for r in response.get("results", []):
                title = r.get("title", "No title")
                snippet = (r.get("content") or "")[:500]
                url = r.get("url", "")
                date = r.get("published_date") or r.get("date") or "Recent"
                line = f"{title} — {snippet} [SOURCE: {url} | {date}]"
                all_results.append(line)
        except Exception as e:
            continue  # Silently continue on one failed query

    if not all_results:
        return "No credible news found in the past 30 days for {ticker} ({business})."

    # Deduplicate by URL
    seen_urls = set()
    deduped = []
    for line in all_results:
        try:
            url_part = line.split("[SOURCE: ")[1].split(" | ")[0]
            if url_part not in seen_urls:
                seen_urls.add(url_part)
                deduped.append(line)
        except IndexError:
            if line not in deduped:
                deduped.append(line)

    return "\n\n".join(deduped[:15])


# The actual tool that gets bound to the agent
search_news_tool = StructuredTool.from_function(
    func=search_recent_stock_news,
    name="search_recent_stock_news",
    description="Runs 3 targeted searches for high-quality stock-specific news from the last 30 days. Returns results with mandatory inline citations.",
    args_schema=NewsSearchInput,
)

# agents/news/tools.py (full file)
# GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG
# from datetime import datetime, timedelta
# from typing import List
# from langchain_core.tools import StructuredTool
# from pydantic import BaseModel, Field
# from tavily import TavilyClient
# import os
# from dotenv import load_dotenv

# load_dotenv()

# class NewsSearchInput(BaseModel):
#     """Input schema for news search tool"""
#     ticker: str = Field(..., description="Stock Ticker (e.g., AAPL)")
#     business: str = Field(..., description="Business/Company Name (e.g., Apple Inc.)")


# def search_recent_stock_news(ticker: str, business: str) -> str:
#     """
#     Targeted searches for recent stock news. Filtered, deduped, concise.
#     """
#     client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

#     queries = [
#         f'"{business} ({ticker})" (earnings OR guidance OR results OR "price target" OR upgrade OR downgrade)',
#         f'"{business} ({ticker})" (stock news OR shares OR revenue)',
#         f'"{business} ({ticker})" (beat OR miss OR growth OR decline)',
#     ]  # Fewer, more focused queries

#     all_results: List[str] = []

#     for query in queries:
#         try:
#             response = client.search(
#                 query=query,
#                 search_depth="basic",  # Faster, less noise than "advanced"
#                 topic="news",
#                 max_results=5,  # Even tighter
#                 days=30,
#                 include_domains=[
#                     "cnbc.com", "bloomberg.com", "reuters.com", "wsj.com",
#                     "finance.yahoo.com", "marketwatch.com"
#                 ],
#                 exclude_domains=["reddit.com", "twitter.com", "x.com"],
#             )

#             for r in response.get("results", []):
#                 title = r.get("title", "No title")
#                 snippet = (r.get("content") or r.get("snippet", ""))[:200]  # Much shorter!
#                 url = r.get("url", "")
#                 date_str = r.get("published_date") or r.get("date") or "Recent"
#                 # Parse date to YYYY-MM-DD if possible
#                 try:
#                     date = datetime.strptime(date_str.split(',')[0], "%d %b %Y").strftime("%Y-%m-%d") if " " in date_str else date_str
#                 except:
#                     date = "Recent"
                
#                 line = f"{title} — {snippet} [SOURCE: {url} | {date}]"
                
#                 # STRICT filter
#                 text_lower = line.lower()
#                 if ticker.lower() not in text_lower and business.lower() not in text_lower:
#                     continue
#                 all_results.append(line)
#         except Exception:
#             continue

#     if not all_results:
#         return f"No recent news for {business} ({ticker}). Neutral due to low volume."

#     # Dedupe + limit
#     seen_urls = set()
#     deduped = []
#     for line in all_results:
#         url_part = line.split("[SOURCE: ")[-1].split(" | ")[0] if "[SOURCE:" in line else ""
#         if url_part not in seen_urls:
#             seen_urls.add(url_part)
#             deduped.append(line)
#         if len(deduped) >= 7:  # Hard cap
#             break

#     return "\n\n".join(deduped)


# search_news_tool = StructuredTool.from_function(
#     func=search_recent_stock_news,
#     name="search_recent_stock_news",
#     description="Fetches 5-7 concise, recent news items for {ticker} ({business}) with citations. Filtered to company mentions only.",
#     args_schema=NewsSearchInput,
# )

# GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG

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