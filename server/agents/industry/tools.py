# # agents/industry/tools.py
# from datetime import datetime, timedelta
# from typing import List
# from langchain_core.tools import StructuredTool
# from pydantic import BaseModel, Field
# from tavily import TavilyClient
# import os
# from dotenv import load_dotenv

# load_dotenv()

# class IndustrySearchInput(BaseModel):
#     ticker: str = Field(..., description="Stock ticker (e.g., NVDA)")
#     industry: str = Field(..., description="Industry/sector name (e.g., Semiconductors)")

# def search_recent_industry_insights(ticker: str, industry: str) -> str:
#     """
#     Search for recent industry/sector trends, reports, and competitive analysis.
#     """
#     client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    
#     query = f"{industry} OR {ticker} sector industry trends outlook competition headwinds tailwinds market share 2025 2026"
    
#     try:
#         response = client.search(
#             query=query,
#             search_depth="advanced",
#             topic="news",                    # Gives accurate published_date + prioritizes fresh content
#             max_results=12,                 
#             time_range="2months",           
#             include_domains=[
#                 "bloomberg.com", "reuters.com", "wsj.com", "ft.com",
#                 "forbes.com", "mckinsey.com", "deloitte.com", "pwc.com",
#                 "statista.com", "morningstar.com", "seekingalpha.com"
#             ],
#             exclude_domains=["reddit.com", "twitter.com", "x.com", "medium.com"],
#         )
        
#         results = response.get("results", [])
#         if not results:
#             return "No significant industry reports or analyses found in the past 60 days. This often indicates neutral/stabilized sentiment."

#         formatted = []
#         for r in results:
#             title = r.get("title", "No title")
#             snippet = r.get("content", "")[:500]
#             url = r.get("url", "")
#             date = r.get("published_date", r.get("date", "Recent"))
#             formatted.append(f"• {title}\n  {snippet}\n  Source: {url} | {date}")

#         return "\n\n".join(formatted)
        
#     except Exception as e:
#         return f"Industry search failed: {str(e)}"

# # Tool definition
# search_industry_tool = StructuredTool.from_function(
#     func=search_recent_industry_insights,
#     name="search_recent_industry_insights",
#     description="Search for the top recent (last 60 days) industry reports, sector analyses, competitive dynamics, and outlook using both company ticker and industry name. Returns formatted articles with titles, snippets, URLs, and published dates.",
#     args_schema=IndustrySearchInput,
# )

# # # agents/industry/tools.py
# # from datetime import datetime, timedelta
# # from typing import Optional
# # from langchain_core.tools import Tool
# # from tavily import TavilyClient
# # import os
# # from dotenv import load_dotenv

# # load_dotenv()  # Load .env for TAVILY_API_KEY

# # def search_recent_industry_insights(query: str, max_results: int = 10, include_domains: list = None, exclude_domains: list = None) -> str:
# #     """
# #     Searches for recent industry reports, analyses, and news using Tavily API.
# #     Optimized for sector insights: trends, competition, dynamics from credible sources.
# #     Returns JSON-like string with top results (title | snippet | url | date).
# #     """
# #     client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    
# #     # 30-day cutoff
# #     cutoff_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
# #     # Tavily params (focus on credible, analytical sources)
# #     response = client.search(
# #         query=query,
# #         search_depth="advanced",  # Deeper for reports/analyses
# #         max_results=max_results,
# #         time_range="month",  # Last 30 days
# #         include_domains=include_domains or ["bloomberg.com", "reuters.com", "wsj.com", "forbes.com", "mckinsey.com", "deloitte.com", "statista.com"],  # Reports + outlets
# #         exclude_domains=exclude_domains or ["reddit.com", "twitter.com", "facebook.com"],  # Avoid social noise
# #         include_answer=False,  # Raw results for analysis
# #     )
    
# #     if not response.get("results"):
# #         return "No recent industry insights found."
    
# #     # Format for easy parsing (title | snippet | url | date)
# #     formatted = []
# #     for result in response["results"]:
# #         date_str = result.get("date", "Unknown date")
# #         formatted.append(f"{result['title']} | {result['content']} | {result['url']} | {date_str}")
    
# #     return "\n".join(formatted)

# # # LangChain Tool for Groq binding
# # search_industry_tool = Tool(
# #     name="search_recent_industry_insights",
# #     description="Search for the top 10 most relevant recent industry reports, analyses, and news for a stock's sector from the last 30 days. Input: a query like 'AAPL industry sector analysis'. Focuses on credible sources (e.g., Bloomberg, McKinsey). Returns: formatted list of title | snippet | URL | date.",
# #     func=search_recent_industry_insights,
# # )

# agents/industry/tools.py
from datetime import datetime, timedelta
from typing import List
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

# class IndustrySearchInput(BaseModel):
#     """Input schema for industry insights tool"""
#     ticker: str = Field(..., description="Stock ticker symbol to analyze its industry/sector")
#     industry: str = Field(..., description="Industry/sector name from Yahoo Finance (e.g., Semiconductors, Internet Retail)")

# def search_recent_industry_insights(ticker: str, industry: str) -> str:
#     """
#     High-precision industry research tool using Tavily.
#     Uses 3 short, powerful, human-written queries proven to surface Bloomberg, Reuters, WSJ, Morningstar, etc.
#     """
#     client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    
#     queries = [
#         f"{ticker} {industry} sector outlook trends 2025 2026",
#         f"{ticker} {industry} competition market share consolidation",
#         f"{ticker} {industry} tailwinds headwinds risks regulation 2025",
#     ]
    
#     all_results = []

#     for query in queries:
#         try:
#             response = client.search(
#                 query=query,
#                 search_depth="advanced",
#                 topic="news",
#                 max_results=8,
#                 time_range="month",  # last ~30 days
#                 include_domains=[
#                     "bloomberg.com", "reuters.com", "wsj.com", "ft.com",
#                     "morningstar.com", "seekingalpha.com", "statista.com",
#                     "mckinsey.com", "deloitte.com", "pwc.com", "forbes.com"
#                 ],
#                 exclude_domains=["reddit.com", "twitter.com", "x.com", "medium.com"],
#             )

#             results = response.get("results", [])
#             for r in results:
#                 title = r.get("title", "No title")
#                 snippet = r.get("content", "")[:550]
#                 url = r.get("url", "")
#                 date = r.get("published_date") or r.get("date") or "Recent"
#                 all_results.append(f"• {title}\n  {snippet}\n  Source: {url} | {date}")

#         except Exception as e:
#             all_results.append(f"Warning: One search failed: {str(e)}")

#     if not all_results:
#         return "No high-quality recent industry reports found in the last 30 days."

#     # Dedupe by URL (simple but effective)
#     seen = set()
#     deduped = []
#     for item in all_results:
#         url = item.split("Source: ")[-1].split(" | ")[0]
#         if url not in seen:
#             seen.add(url)
#             deduped.append(item)

#     return "\n\n".join(deduped)


# # Tool definition
# search_industry_tool = StructuredTool.from_function(
#     func=search_recent_industry_insights,
#     name="search_recent_industry_insights",
#     description="Performs 3 targeted searches for the latest high-quality industry/sector reports, competitive dynamics, and tailwinds/headwinds (last 30 days only). Returns rich, cited results from Bloomberg, Reuters, WSJ, etc.",
#     args_schema=IndustrySearchInput,
# )

class IndustrySearchInput(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol (e.g., NVDA)")
    industry: str = Field(..., description="Industry/sector name from Yahoo Finance (e.g., Semiconductors)")


def search_recent_industry_insights(ticker: str, industry: str) -> str:
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    queries = [
        # f"{ticker} {industry} sector outlook OR forecast OR trends 2025 2026",
        # f"{ticker} {industry} competition OR market share OR consolidation 2025",
        # f"{ticker} {industry} tailwinds OR headwinds OR regulation OR risks 2025",
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
                # Citation on the SAME line → model can't lose it
                all_results.append(f"{title} — {snippet} [SOURCE: {url} | {date}]")
        except Exception:
            continue

    if not all_results:
        return "No credible industry reports found in the past 30 days."

    # Dedupe
    seen = set()
    deduped = []
    for line in all_results:
        key = line.split("[SOURCE: ")[-1].split(" | ")[0] if "[SOURCE:" in line else line
        if key not in seen:
            seen.add(key)
            deduped.append(line)

    return "\n\n".join(deduped[:15])


# THIS IS THE LINE THAT WAS MISSING → creates the actual tool
search_industry_tool = StructuredTool.from_function(
    func=search_recent_industry_insights,
    name="search_recent_industry_insights",
    description="Runs 3 targeted searches for high-quality industry reports from the last 30 days. Returns cited results.",
    args_schema=IndustrySearchInput,
)
