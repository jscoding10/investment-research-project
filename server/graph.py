from langchain_core.runnables import RunnableLambda
from langgraph.graph import END, StateGraph, START
from langgraph.cache.memory import InMemoryCache
from dotenv import load_dotenv
from fastapi import HTTPException

from agents.evaluation.agent import evaluate_aggregated_sentement
# from agents.filings.agent import get_filings_sentiment
# from data.util.ingest_sec_filings import ensure_filings_ingested
from agents.news.agent import get_news_sentiment
from agents.industry.agent import get_industry_sentiment
from agents.aggregation.agent import get_aggregated_sentiment
from agents.peer.agent import get_peer_sentiment
from util.logger import get_logger
from models.state import EquityResearchState
from agents.fundamentals.agent import get_fundamental_sentiment
from agents.macro.agent import get_macro_sentiment
from agents.technical.agent import get_technical_sentiment
from util.validation import validate_ticker
from util.diagrams import draw_architecture
from util.cache import (
    create_cache_policy,
    create_fundamentals_cache_policy,
    create_macro_cache_policy,
    create_technical_cache_policy,
)
from util.formatting import format_sentiment_output
from util.logger import get_logger

load_dotenv()
logger = get_logger(__name__)


# graph nodes
def ticker_validation(state: EquityResearchState) -> dict:
    """Validation node to ensure we have a real ticker"""
    logger.info(f"Validating ticker: {state.ticker}")
    result = validate_ticker(ticker=state.ticker, state=state)
    logger.info(f"Ticker validation complete for {state.ticker}")
    return result

# def filings_ingestion(state: EquityResearchState) -> dict:
#     """Ingest SEC filings into vector store before research agents run"""
#     logger.info(f"Starting SEC filings ingestion for {state.ticker}")
#     try:
#         was_ingested = ensure_filings_ingested(ticker=state.ticker)
#         if was_ingested:
#             logger.info(f"SEC filings ingested for {state.ticker}")
#         else:
#             logger.info(f"SEC filings already available for {state.ticker}")
#         return {"filings_ingested": True}
#     except Exception as e:
#         logger.error(
#             f"SEC filings ingestion failed for {state.ticker}: {e}", exc_info=True
#         )
#         return {"filings_ingested": False}

# def ticker_router(state: EquityResearchState):
#     """Route to filings ingestion if ticker is valid, otherwise end"""
#     if state.is_ticker_valid:
#         return "filings_ingestion"
#     else:
#         return END
        

# def filings_ingestion_router(state: EquityResearchState):
#     """Route to all research agents in parallel after filings ingestion"""
#     return [
#         "fundamental_research_agent",
#         "technical_research_agent",
#         "macro_research_agent",
#         "industry_research_agent",
#         "peer_research_agent",
#         "headline_research_agent",
#         "filings_research_agent",
#     ]

def ticker_router(state: EquityResearchState):
    if state.is_ticker_valid:
        return [
            "fundamental_research_agent",
            "technical_research_agent",
            "macro_research_agent",
            "industry_research_agent",
            "peer_research_agent",
            "news_research_agent",
            # "filings_research_agent",
        ]
    else:
        return END
    
def fundamental_research_agent(state: EquityResearchState) -> dict:
    """LLM call to generate fundamental research sentiment"""
    logger.info(f"Starting fundamental research for {state.ticker}")
    try:
        fundamental_sentiment = get_fundamental_sentiment(
            ticker=state.ticker,
            cached_info=state.ticker_info,  # Pass cached yfinance info to avoid duplicate API call
        )
        logger.info(f"Completed fundamental research for {state.ticker}")
        return {"fundamental_sentiment": format_sentiment_output(fundamental_sentiment)}
    except Exception as e:
        logger.error(
            f"Fundamental research failed for {state.ticker}: {e}", exc_info=True
        )
        return {
            "fundamental_sentiment": "Analysis unavailable due to data retrieval error."
        }


def technical_research_agent(state: EquityResearchState) -> dict:
    """LLM call to generate technical research sentiment"""
    logger.info(f"Starting technical research for {state.ticker}")
    try:
        technical_sentiment = get_technical_sentiment(
            ticker=state.ticker,
        )
        logger.info(f"Completed technical research for {state.ticker}")
        return {"technical_sentiment": format_sentiment_output(technical_sentiment)}
    except Exception as e:
        logger.error(
            f"Technical research failed for {state.ticker}: {e}", exc_info=True
        )
        return {
            "technical_sentiment": "Analysis unavailable due to data retrieval error."
        }


def macro_research_agent(state: EquityResearchState) -> dict:
    """LLM call to generate macro research sentiment"""
    logger.info("Starting macro research")
    try:
        macro_sentiment = get_macro_sentiment()
        logger.info("Completed macro research")
        return {"macro_sentiment": format_sentiment_output(macro_sentiment)}
    except Exception as e:
        logger.error(f"Macro research failed: {e}", exc_info=True)
        return {"macro_sentiment": "Analysis unavailable due to data retrieval error."}


def industry_research_agent(state: EquityResearchState) -> dict:
    """LLM call to generate industry research sentiment"""
    logger.info(f"Starting industry research for {state.ticker}")
    try:
        industry_sentiment = get_industry_sentiment(
            ticker=state.ticker, industry=state.industry
        )
        logger.info(f"Completed industry research for {state.ticker}")
        return {"industry_sentiment": industry_sentiment}
    except Exception as e:
        logger.error(f"Industry research failed for {state.ticker}: {e}", exc_info=True)
        return {
            "industry_sentiment": "Analysis unavailable due to data retrieval error."
        }

def peer_research_agent(state: EquityResearchState) -> dict:
    """LLM call to generate peer research sentiment"""
    logger.info(f"Starting peer research for {state.business}")
    try:
        peer_sentiment = get_peer_sentiment(ticker=state.ticker, business=state.business)
        logger.info(f"Completed peer research for {state.business}")
        return {"peer_sentiment": peer_sentiment}
    except Exception as e:
        logger.error(f"Peer research failed for {state.business}: {e}", exc_info=True)
        return {"peer_sentiment": "Analysis unavailable due to data retrieval error."}



def news_research_agent(state: EquityResearchState) -> dict:
    """LLM call to generate technical research sentiment"""
    logger.info(f"Starting headline research for {state.business}")
    try: 
        news_sentiment = get_news_sentiment(
            ticker=state.ticker,
            business=state.business
        )
        logger.info(f"Completed headline research for {state.business}")
        return {"news_sentiment": news_sentiment}
    except Exception as e:
        logger.error(
            f"News research failed for {state.business}: {e}", exc_info=True
        )
        return {
            "news_sentiment": "Analysis unavailable due to data retrieval error."
        }
    
# def filings_research_agent(state: EquityResearchState) -> dict:
#     """LLM call to generate SEC filings research sentiment"""
#     logger.info(f"Starting filings research for {state.ticker}")
#     try:
#         filings_sentiment = get_filings_sentiment(ticker=state.ticker)
#         if filings_sentiment:
#             logger.info(f"Completed filings research for {state.ticker}")
#             return {"filings_sentiment": format_sentiment_output(filings_sentiment)}
#         else:
#             return {"filings_sentiment": "No SEC filings available for analysis."}
#     except Exception as e:
#         logger.error(f"Filings research failed for {state.ticker}: {e}", exc_info=True)
#         return {
#             "filings_sentiment": "Analysis unavailable due to data retrieval error."
#         }    


def sentiment_aggregator(state: EquityResearchState) -> dict:
    """LLM call to aggregate research findings and synthesize sentiment"""
    logger.info(f"Starting sentiment aggregation for {state.ticker}")
    try:
        combined_sentiment = get_aggregated_sentiment(state)
        logger.info(f"Completed sentiment aggregation for {state.ticker}")
        return {"combined_sentiment": combined_sentiment}
    except Exception as e:
        logger.error(
            f"Sentiment aggregation failed for {state.ticker}: {e}", exc_info=True
        )
        return {
            "combined_sentiment": (
                f"**Conclusion:** Unable to fully synthesize sentiment due to an internal error. "
                f"Please review individual research components for partial analysis."
            )
        }

def sentiment_evaluator(state: EquityResearchState) -> dict:
    """LLM call to evaluate sentiment aggregator output"""
    logger.info("Starting sentiment evaluation")
    try:
        sentiment_evaluation = evaluate_aggregated_sentement(
            sentiment=state.combined_sentiment
        )
        logger.info("Completed sentiment evaluation")
        sentiment_evaluation["revision_iteration_count"] = (
            state.revision_iteration_count + 1
        )
        return sentiment_evaluation
    except Exception as e:
        logger.error(f"Sentiment evaluation failed: {e}", exc_info=True)
        # Mark as compliant to avoid infinite retry loops - log the failure
        return {
            "compliant": True,
            "feedback": "Evaluation skipped due to internal error.",
            "revision_iteration_count": state.revision_iteration_count + 1,
        }


def sentiment_router(state: EquityResearchState):
    "Route back to aggregator or terminate based on evaluator feedback"
    if state.compliant == True:
        return "Compliant"
    elif state.revision_iteration_count > 2:
        return "Compliant"
    else:
        return "Noncompliant"


# build workflow
graph_builder = StateGraph(EquityResearchState)

# add agent nodes
graph_builder.add_node("ticker_validation", ticker_validation)
# graph_builder.add_node("filings_ingestion", filings_ingestion)

graph_builder.add_node(
    "fundamental_research_agent",
    fundamental_research_agent,
    # Dynamic cache: shorter TTL when earnings are imminent, key changes on earnings status
    cache_policy=create_fundamentals_cache_policy(),
)

graph_builder.add_node(
    "technical_research_agent",
    technical_research_agent,
    # Dynamic cache: key includes hour bucket for time-sensitive price data
    cache_policy=create_technical_cache_policy(),
)

graph_builder.add_node(
    "macro_research_agent",
    macro_research_agent,
    # Dynamic cache: key includes date bucket for daily invalidation
    cache_policy=create_macro_cache_policy(),
)

graph_builder.add_node(
    "industry_research_agent",
    industry_research_agent,
    # evict industry research cache after one hour
    cache_policy=create_cache_policy(ttl=3600),
)

graph_builder.add_node(
    "peer_research_agent",
    peer_research_agent,
    # evict peer research cache after one hour
    cache_policy=create_cache_policy(ttl=3600),
)

graph_builder.add_node(
    "news_research_agent",
    news_research_agent,
    # evict news research cache after one hour
    cache_policy=create_cache_policy(ttl=3600),
)

# graph_builder.add_node(
#     "filings_research_agent",
#     filings_research_agent,
#     # evict filings research cache after one day
#     cache_policy=create_cache_policy(ttl=86400),
# )

graph_builder.add_node(
    "aggregator",
    sentiment_aggregator,
)

graph_builder.add_node("evaluator", sentiment_evaluator)

# validate ticker, ingest filings, then call research agents in parallel
# graph_builder.add_edge(START, "ticker_validation")
# graph_builder.add_conditional_edges(
#     "ticker_validation",
#     ticker_router,
#     ["filings_ingestion", END],
# )
# # ingest SEC filings before research agents run, then fan out to all agents
# graph_builder.add_conditional_edges(
#     "filings_ingestion",
#     filings_ingestion_router,

# call research agents in parallel when ticker validation passes, otherwise end

graph_builder.add_edge(START, "ticker_validation")
graph_builder.add_conditional_edges(
    "ticker_validation",
    ticker_router,
    [
        "fundamental_research_agent",
        "technical_research_agent",
        "macro_research_agent",
        "industry_research_agent",
        "peer_research_agent",
        "news_research_agent",
        # "filings_research_agent",
        END,
    ],
)

# synthesize sentiment
graph_builder.add_edge("fundamental_research_agent", "aggregator")
graph_builder.add_edge("technical_research_agent", "aggregator")
graph_builder.add_edge("macro_research_agent", "aggregator")
graph_builder.add_edge("industry_research_agent", "aggregator")
graph_builder.add_edge("peer_research_agent", "aggregator")
graph_builder.add_edge("news_research_agent", "aggregator")
# graph_builder.add_edge("filings_research_agent", "aggregator")
graph_builder.add_edge("aggregator", "evaluator")
graph_builder.add_conditional_edges(
    "evaluator", sentiment_router, {"Compliant": END, "Noncompliant": "aggregator"}
)

# compile the graph workflow with node caching
cache = InMemoryCache()

graph_workflow = graph_builder.compile(cache=cache)

# uncomment to regenerate architectural diagram

# draw_architecture(graph_workflow)


def input(input_dict: dict) -> EquityResearchState:
    state = EquityResearchState(
        ticker=input_dict["ticker"],
        trade_duration=input_dict["trade_duration"],
        trade_direction=input_dict["trade_direction"],
        industry="",
        business="",
        fundamental_sentiment="",
        technical_sentiment="",
        macro_sentiment="",
        industry_sentiment="",
        peer_sentiment="",
        news_sentiment="",
        # filings_sentiment="",
        combined_sentiment="",
        compliant=False,
        feedback=None,
        is_ticker_valid=False,
        revision_iteration_count=0,
        ticker_info=None,  # Will be populated by ticker_validation node
        # filings_ingested=False
    )
    return state


def output(state: dict | EquityResearchState) -> EquityResearchState:
    if isinstance(state, dict):
        state = EquityResearchState(**state)

    if not state.is_ticker_valid:
        raise HTTPException(status_code=400, detail=f"Ticker {state.ticker} is invalid")
    return state


# pipeline to interface with the API
research_chain = RunnableLambda(input) | graph_workflow | RunnableLambda(output)