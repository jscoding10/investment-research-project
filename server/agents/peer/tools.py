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

    queries = [
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

    seen = set()
    deduped = []
    for line in all_results:
        key = line.split("[SOURCE: ")[-1].split(" | ")[0] if "[SOURCE:" in line else line
        if key not in seen:
            seen.add(key)
            deduped.append(line)

    return "\n\n".join(deduped[:15])

search_peer_tool = StructuredTool.from_function(
    func=search_recent_peer_insights,
    name="search_recent_peer_insights",
    description="Finds recent articles comparing a company to its direct peers (earnings, guidance, valuation, market share). Uses both ticker and company name for best results.",
    args_schema=PeerSearchInput,
)