from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

class IndustrySearchInput(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol (e.g., NVDA)")
    industry: str = Field(..., description="Industry/sector name from Yahoo Finance (e.g., Semiconductors)")


def search_recent_industry_insights(ticker: str, industry: str) -> str:
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    queries = [
        f"{industry} industry sector analysis",
        f"{industry} market trends",
    ]

    all_results = []

    for query in queries:
        try:
            response = client.search(
                query=query,
                search_depth="advanced",
                topic="news",
                max_results=8,
                time_range="month",
                include_domains=[
                    "bloomberg.com", "reuters.com", "wsj.com", "ft.com",
                    "morningstar.com", "seekingalpha.com", "statista.com",
                    "mckinsey.com", "deloitte.com", "pwc.com"
                ],
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
        return "No credible industry reports found in the past 30 days."

    seen = set()
    deduped = []
    for line in all_results:
        key = line.split("[SOURCE: ")[-1].split(" | ")[0] if "[SOURCE:" in line else line
        if key not in seen:
            seen.add(key)
            deduped.append(line)

    return "\n\n".join(deduped[:15])

search_industry_tool = StructuredTool.from_function(
    func=search_recent_industry_insights,
    name="search_recent_industry_insights",
    description="Runs 3 targeted searches for high-quality industry reports from the last 30 days. Returns cited results.",
    args_schema=IndustrySearchInput,
)
