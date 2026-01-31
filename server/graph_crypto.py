from langchain_core.runnables import RunnableLambda
from langgraph.graph import END, StateGraph, START
from langgraph.cache.memory import InMemoryCache
from dotenv import load_dotenv
from fastapi import HTTPException

from agents.crypto.evaluation.agent_crypto import evaluate_aggregated_sentement
from agents.crypto.news.agent_crypto import get_news_sentiment
from agents.crypto.aggregation.agent_crypto import get_aggregated_sentiment
from agents.crypto.peer.agent_crypto import get_peer_sentiment
from util.logger import get_logger
from models.crypto.state_crypto import CryptoResearchState
from agents.crypto.macro.agent_crypto import get_macro_sentiment
from agents.crypto.technical.agent_crypto import get_technical_sentiment
from util.crypto.validation_crypto import validate_ticker
from util.diagrams import draw_architecture
from util.crypto.cache_crypto import (
    create_cache_policy,
    create_macro_cache_policy,
    create_technical_cache_policy,
)
from util.crypto.formatting_crypto import format_sentiment_output
from util.logger import get_logger

load_dotenv()
logger = get_logger(__name__)


# graph nodes
def ticker_validation(state: CryptoResearchState) -> dict:
    """Validation node to ensure we have a real ticker"""
    logger.info(f"Validating ticker: {state.ticker}")
    result = validate_ticker(ticker=state.ticker, state=state)
    logger.info(f"Ticker validation complete for {state.ticker}")
    return result

def ticker_router(state: CryptoResearchState):
    if state.is_ticker_valid:
        return [
            "technical_research_agent",
            "macro_research_agent",
            "peer_research_agent",
            "news_research_agent",
        ]
    else:
        return END
    
def technical_research_agent(state: CryptoResearchState) -> dict:
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


def macro_research_agent(state: CryptoResearchState) -> dict:
    """LLM call to generate macro research sentiment"""
    logger.info("Starting macro research")
    try:
        macro_sentiment = get_macro_sentiment()
        logger.info("Completed macro research")
        return {"macro_sentiment": format_sentiment_output(macro_sentiment)}
    except Exception as e:
        logger.error(f"Macro research failed: {e}", exc_info=True)
        return {"macro_sentiment": "Analysis unavailable due to data retrieval error."}

def peer_research_agent(state: CryptoResearchState) -> dict:
    """LLM call to generate peer research sentiment"""
    logger.info(f"Starting peer research for {state.name}")
    try:
        peer_sentiment = get_peer_sentiment(ticker=state.ticker, name=state.name)
        logger.info(f"Completed peer research for {state.name}")
        return {"peer_sentiment": peer_sentiment}
    except Exception as e:
        logger.error(f"Peer research failed for {state.name}: {e}", exc_info=True)
        return {"peer_sentiment": "Analysis unavailable due to data retrieval error."}



def news_research_agent(state: CryptoResearchState) -> dict:
    """LLM call to generate technical research sentiment"""
    logger.info(f"Starting news research for {state.name}")
    try: 
        news_sentiment = get_news_sentiment(
            ticker=state.ticker,
            name=state.name
        )
        logger.info(f"Completed news research for {state.name}")
        return {"news_sentiment": news_sentiment}
    except Exception as e:
        logger.error(
            f"News research failed for {state.name}: {e}", exc_info=True
        )
        return {
            "news_sentiment": "Analysis unavailable due to data retrieval error."
        }
    
def sentiment_aggregator(state: CryptoResearchState) -> dict:
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

def sentiment_evaluator(state: CryptoResearchState) -> dict:
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


def sentiment_router(state: CryptoResearchState):
    "Route back to aggregator or terminate based on evaluator feedback"
    if state.compliant == True:
        return "Compliant"
    elif state.revision_iteration_count > 2:
        return "Compliant"
    else:
        return "Noncompliant"


# build workflow
graph_builder = StateGraph(CryptoResearchState)

# add agent nodes
graph_builder.add_node("ticker_validation", ticker_validation)

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

graph_builder.add_node(
    "aggregator",
    sentiment_aggregator,
)

graph_builder.add_node("evaluator", sentiment_evaluator)

graph_builder.add_edge(START, "ticker_validation")
graph_builder.add_conditional_edges(
    "ticker_validation",
    ticker_router,
    [
        "technical_research_agent",
        "macro_research_agent",
        "peer_research_agent",
        "news_research_agent",
        END,
    ],
)

# synthesize sentiment
graph_builder.add_edge("technical_research_agent", "aggregator")
graph_builder.add_edge("macro_research_agent", "aggregator")
graph_builder.add_edge("peer_research_agent", "aggregator")
graph_builder.add_edge("news_research_agent", "aggregator")
graph_builder.add_edge("aggregator", "evaluator")
graph_builder.add_conditional_edges(
    "evaluator", sentiment_router, {"Compliant": END, "Noncompliant": "aggregator"}
)

# compile the graph workflow with node caching
cache = InMemoryCache()

graph_workflow = graph_builder.compile(cache=cache)

# uncomment to regenerate architectural diagram

# draw_architecture(graph_workflow)

def input(input_dict: dict) -> CryptoResearchState:
    state = CryptoResearchState(
        ticker=input_dict["ticker"],
        trade_duration=input_dict["trade_duration"],     
        trade_direction=input_dict["trade_direction"],  
        name="",
        technical_sentiment="",
        macro_sentiment="",
        peer_sentiment="",
        news_sentiment="",
        combined_sentiment="",
        compliant=False,
        feedback=None,
        is_ticker_valid=False,
        revision_iteration_count=0,
        ticker_info=None,
    )
    return state

def output(state: dict | CryptoResearchState) -> CryptoResearchState:
    if isinstance(state, dict):
        state = CryptoResearchState(**state)

    if not state.is_ticker_valid:
        raise HTTPException(status_code=400, detail=f"Ticker {state.ticker} is invalid")
    return state


# pipeline to interface with the API
research_chain_crypto = RunnableLambda(input) | graph_workflow | RunnableLambda(output)