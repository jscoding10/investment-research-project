import dotenv
from datetime import datetime, timedelta
from langchain_groq import ChatGroq

from agents.shared.agent_utils import run_agent_with_tools  
from agents.shared.llm_models import LLM_MODELS
from agents.news.prompt import news_research_prompt
from agents.news.tools import search_news_tool


dotenv.load_dotenv()


def get_news_sentiment(ticker: str, business: str):
    """
    Get news sentiment using Groq + Tavily search tool.
    Groq analyzes the fetched news for bullish/bearish/neutral.
    """

    current_date = datetime.now().strftime("%Y-%m-%d")
    cutoff_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    prompt = news_research_prompt.format(
        ticker=ticker,
        business=business,
        current_date=current_date,
        cutoff_date=cutoff_date,
    )
    model = LLM_MODELS["groq-llama"]

    llm = ChatGroq(
        model=model,
        temperature=0.0, 
         # Low randomness for consistent analysis
        # api_key automatically loaded from .env → GROQ_API_KEY
    )

    # Run with the search tool (Groq will call it automatically if needed)
    tools = [search_news_tool]
    result = run_agent_with_tools(llm=llm, prompt=prompt, tools=tools)

    return result

# Your main file (e.g., agents/news/agent.py)

# agents/news/agent.py   ← replace your current file with this

# import dotenv
# import re
# from datetime import datetime, timedelta
# from langchain_groq import ChatGroq
# from langchain_core.messages import HumanMessage, ToolMessage, AIMessage

# from agents.news.tools import search_news_tool
# from agents.news.prompt import news_research_prompt
# from agents.shared.llm_models import LLM_MODELS

# dotenv.load_dotenv()


# def get_news_sentiment(ticker: str, business: str) -> str:
#     current_date = datetime.now().strftime("%Y-%m-%d")
#     cutoff_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

#     prompt = news_research_prompt.format(
#         ticker=ticker,
#         business=business,
#         current_date=current_date,
#         cutoff_date=cutoff_date,
#     )

#     llm = ChatGroq(
#         model=LLM_MODELS["groq-llama"],
#         temperature=0.0,
#         max_tokens=1000,
#     )

#     llm_with_tools = llm.bind_tools([search_news_tool], tool_choice="auto")

#     # Step 1: Send prompt → LLM decides to call tool
#     response = llm_with_tools.invoke([HumanMessage(content=prompt)])

#     # Step 2: If tool was called → execute it and feed result back
#     if response.tool_calls:
#         tool_call = response.tool_calls[0]
#         if tool_call["name"] == "search_recent_stock_news":
#             args = tool_call["args"]
#             # ←←← THIS WAS THE BUG: use .func, not the tool object
#             news_text = search_news_tool.func(ticker=args["ticker"], business=args["business"])

#             # Build proper message history
#             messages = [
#                 HumanMessage(content=prompt),
#                 response,  # AIMessage with tool call
#                 ToolMessage(content=news_text, tool_call_id=tool_call["id"]),
#             ]

#             final_response = llm_with_tools.invoke(messages)
#             raw_output = final_response.content
#         else:
#             raw_output = response.content
#     else:
#         raw_output = response.content

#     return _parse_and_clean_output(raw_output, ticker, business)


# def _parse_and_clean_output(raw: str, ticker: str, business: str) -> str:
#     if not raw.strip():
#         return "[SENTIMENT: NEUTRAL]\n\nNo data.\nConfidence: Low"

#     # Extract sentiment
#     sent_match = re.search(r"\[SENTIMENT:\s*(BULLISH|BEARISH|NEUTRAL)", raw, re.I)
#     sentiment = sent_match.group(1).upper() if sent_match else None

#     # Extract scored bullets
#     bullets = re.findall(
#         r"\*\s*\[([+-]1|0)\]\s*(.+?)\s*\[SOURCE:\s*(https?://[^\s|]+)\s*\|\s*([^\]]+)", 
#         raw
#     )

#     if not bullets:
#         return "[SENTIMENT: NEUTRAL]\n\nNo clear signals.\nConfidence: Low"

#     evidence = ""
#     net = bull = bear = 0
#     for tone, text, url, date in bullets:
#         evidence += f"* [{tone}] {text.strip()} [SOURCE: {url} | {date.strip()}]\n"
#         if tone == "+1":
#             net += 1
#             bull += 1
#         elif tone == "-1":
#             net -= 1
#             bear += 1

#     if sentiment is None:
#         sentiment = "BULLISH" if net > 0 else "BEARISH" if net < 0 else "NEUTRAL"

#     conf = "High" if len(bullets) >= 3 else "Medium" if len(bullets) >= 2 else "Low"

#     return (f"[SENTIMENT: {sentiment}]\n\n"
#             f"Evidence:\n{evidence}"
#             f"Net Score: {net} ({bull} bullish, {bear} bearish)\n"
#             f"Confidence: {conf}")