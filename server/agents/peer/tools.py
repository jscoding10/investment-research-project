# from datetime import datetime, timedelta
# from langchain_core.tools import StructuredTool
# from pydantic import BaseModel, Field
# from tavily import TavilyClient
# import os
# from dotenv import load_dotenv

# load_dotenv()

# class PeerSearchInput(BaseModel):
#     """Input schema for peer search tool"""
#     ticker: str = Field(..., description="Stock ticker symbol (e.g., MSFT)")

# def search_recent_peer_insights(ticker: str) -> str:
#     client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    
#     query = f"{ticker} vs competitors OR peers OR peer comparison OR earnings vs peers OR valuation vs peers OR market share shift"
    
#     try:
#         response = client.search(
#             query=query,
#             search_depth="advanced",
#             topic="news",
#             max_results=10,
#             time_range="month",  # ← 30 days
#             include_domains=[
#                 "cnbc.com", "bloomberg.com", "reuters.com", "wsj.com",
#                 "finance.yahoo.com", "seekingalpha.com", "morningstar.com", "barrons.com"
#             ],
#             exclude_domains=["reddit.com", "twitter.com", "x.com", "medium.com"],
#         )
        
#         results = response.get("results", [])
#         if not results:
#             return "No recent peer comparison articles found in the last 30 days."

#         formatted = []
#         for r in results:
#             title = r.get("title", "No title")
#             snippet = r.get("content", "")[:450]
#             url = r.get("url", "")
#             date = r.get("published_date", r.get("date", "Recent"))
#             formatted.append(f"• {title}\n  {snippet}\n  Source: {url} | {date}")

#         return "\n\n".join(formatted)
        
#     except Exception as e:
#         return f"Peer search failed: {str(e)}"

# # Clean, short name — just like your industry tool
# search_peer_tool = StructuredTool.from_function(
#     func=search_recent_peer_insights,
#     name="search_recent_peer_insights",
#     description="Search for recent articles comparing a stock ticker to its direct competitors (performance, valuation, earnings, market share) from the last 30 days.",
#     args_schema=PeerSearchInput,
# )

# agents/peer/tools.py
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

class PeerSearchInput(BaseModel):
    ticker: str = Field(..., description="Stock ticker (e.g., MSFT, NVDA)")
    business: str = Field(..., description="Company name (e.g., Microsoft, NVIDIA)")


def search_recent_peer_insights(ticker: str, business: str) -> str:
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    # 3 targeted queries — proven to work perfectly with Tavily in 2025
    queries = [
        # f'"{business}" OR "{ticker}" peers OR competitors OR "vs " OR comparison earnings OR guidance OR valuation 2025',
        # f'"{business}" OR "{ticker}" market share OR "beats peers" OR "lags peers" OR "outperforming" OR "underperforming" 2025',
        # f'"{business}" OR "{ticker}" analyst OR "relative to peers" OR "peer group" OR "better than" OR "worse than" 2025',
        # f"top competitors of {business}",
        f"{business} vs peers financial comparison",
        f"{business} valuation vs competitors"
    ]

    all_results = []

    for query in queries:
        try:
            response = client.search(
                query=query,
                search_depth="advanced",
                topic="news",
                max_results=10,
                time_range="month",
                include_domains=[
                    "bloomberg.com", "reuters.com", "wsj.com", "ft.com",
                    "cnbc.com", "investing.com", "morningstar.com",
                    "seekingalpha.com", "theinformation.com", "barrons.com"
                ],
                exclude_domains=["reddit.com", "twitter.com", "x.com"],
            )

            for r in response.get("results", []):
                title = r.get("title", "No title")
                snippet = r.get("content", "")[:500]
                url = r.get("url", "")
                date = r.get("published_date") or r.get("date") or "2025"
                all_results.append(f"{title} — {snippet} [SOURCE: {url} | {date}]")
        except Exception:
            continue

    if not all_results:
        return "No recent peer comparison articles found in the last 30 days."

    # Dedupe by URL
    seen = set()
    deduped = []
    for line in all_results:
        key = line.split("[SOURCE: ")[-1].split(" | ")[0] if "[SOURCE:" in line else line
        if key not in seen:
            seen.add(key)
            deduped.append(line)

    return "\n\n".join(deduped[:15])


# The actual tool
search_peer_tool = StructuredTool.from_function(
    func=search_recent_peer_insights,
    name="search_recent_peer_insights",
    description="Finds recent articles comparing a company to its direct peers (earnings, guidance, valuation, market share). Uses both ticker and company name for best results.",
    args_schema=PeerSearchInput,
)