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
            continue 

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

search_news_tool = StructuredTool.from_function(
    func=search_recent_stock_news,
    name="search_recent_stock_news",
    description="Runs 3 targeted searches for high-quality stock-specific news from the last 30 days. Returns results with mandatory inline citations.",
    args_schema=NewsSearchInput,
)