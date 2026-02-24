from langchain_core.runnables import RunnableLambda
from langgraph.graph import END, StateGraph, START
from langgraph.cache.memory import InMemoryCache
from dotenv import load_dotenv
from fastapi import HTTPException

from agents.real_estate.data_retrieval.agent_real_estate import data_retrieval_agent
from agents.real_estate.financial.agent_real_estate import get_financial_analysis
from agents.real_estate.market_trends.agent_real_estate import get_market_trends   
from agents.real_estate.risk.agent_real_estate import get_risk_assessment 
from agents.real_estate.aggregation.agent_real_estate import get_aggregated_analysis  
from agents.real_estate.evaluation.agent_real_estate import evaluate_aggregated_analysis   

from util.logger import get_logger
from models.real_estate.state_real_estate import RealEstateResearchState
from util.real_estate.formatting_real_estate import format_analysis_output

from util.real_estate.cache_real_estate import (
    create_property_cache_policy,
    create_financial_cache_policy,
    create_market_cache_policy,
    create_risk_cache_policy,
)

load_dotenv()
logger = get_logger(__name__)


# ── Nodes ────────────────────────────────────────────────────────────────

def data_retrieval_node(state: RealEstateResearchState) -> dict:
    """Fetch core property data from external APIs (Zillow, RentCast, etc.)"""
    logger.info(f"Starting data retrieval for {state.address}")
    try:
        result = data_retrieval_agent(state)
        logger.info(f"Data retrieval complete for {state.address} - ZPID: {state.zpid}")
        return result
    except Exception as e:
        logger.error(f"Data retrieval failed for {state.address}: {e}", exc_info=True)
        return {"data_retrieved": False}


def data_retrieval_router(state: RealEstateResearchState):
    """Route to financial + market agents only if core data was successfully retrieved"""
    if state.data_retrieved:
        return ["financial_analysis_agent", "market_trends_agent", "risk_assessment_agent"]
    else:
        return END


def financial_analysis_agent(state: RealEstateResearchState) -> dict:
    """Generate financial/investment analysis (cap rate, cash flow, ROI, etc.)"""
    logger.info(f"Starting financial analysis for {state.address}")
    try:
        analysis = get_financial_analysis(state)
        logger.info(f"Completed financial analysis for {state.address}")
        return {"financial_analysis": format_analysis_output(analysis)}
    except Exception as e:
        logger.error(f"Financial analysis failed: {e}", exc_info=True)
        return {"financial_analysis": "Analysis unavailable due to data retrieval error."}


def market_trends_agent(state: RealEstateResearchState) -> dict:
    """Generate market trends analysis using Groq Compound + Zillow grounding"""
    logger.info(f"Starting market trends for {state.address}")
    try:
        trends = get_market_trends(state)
        logger.info(f"Completed market trends for {state.address}")
        return {"market_trends": format_analysis_output(trends)}
    except Exception as e:
        logger.error(f"Market trends failed: {e}", exc_info=True)
        return {"market_trends": "Analysis unavailable due to data retrieval error."}

def risk_assessment_agent(state: RealEstateResearchState) -> dict:
    """Generate risk/livability assessment (crime + schools + context)"""
    logger.info(f"Starting risk assessment for {state.address}")
    try:
        risk = get_risk_assessment(state)
        logger.info(f"Completed risk assessment for {state.address}")
        return {"risk_assessment": format_analysis_output(risk)}
    except Exception as e:
        logger.error(f"Risk assessment failed: {e}", exc_info=True)
        return {"risk_assessment": "Risk assessment unavailable due to data retrieval error."}


def sentiment_aggregator(state: RealEstateResearchState) -> dict:
    """LLM call to aggregate research findings and synthesize sentiment"""
    logger.info(f"Starting sentiment aggregation for {state.address}")
    try:
        combined_sentiment = get_aggregated_analysis(state)
        logger.info(f"Completed sentiment aggregation for {state.address}")
        return {"combined_analysis": combined_sentiment}
    except Exception as e:
        logger.error(
            f"Sentiment aggregation failed for {state.address}: {e}", exc_info=True
        )
        return {
            "combined_analysis": (
                f"**Conclusion:** Unable to fully synthesize sentiment due to an internal error. "
                f"Please review individual research components for partial analysis."
            )
        }

def sentiment_evaluator(state: RealEstateResearchState) -> dict:
    """LLM call to evaluate sentiment aggregator output"""
    logger.info("Starting sentiment evaluation")
    try:
        sentiment_evaluation = evaluate_aggregated_analysis(
            analysis=state.combined_analysis
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


def sentiment_router(state: RealEstateResearchState):
    "Route back to aggregator or terminate based on evaluator feedback"
    if state.compliant == True:
        return END
    elif state.revision_iteration_count > 2:
        return END
    else:
        return "sentiment_aggregator"


# ── Graph Definition ─────────────────────────────────────────────────────

graph_builder = StateGraph(RealEstateResearchState)

# Active nodes 
graph_builder.add_node(
    "data_retrieval",
    data_retrieval_node,
    cache_policy=create_property_cache_policy(),   
)

graph_builder.add_node(
    "financial_analysis_agent",
    financial_analysis_agent,
    cache_policy=create_financial_cache_policy(),  
)

graph_builder.add_node(
    "market_trends_agent",
    market_trends_agent,
    cache_policy=create_market_cache_policy(),    
)

graph_builder.add_node(
    "risk_assessment_agent",
    risk_assessment_agent,
    cache_policy=create_risk_cache_policy(),       
)
graph_builder.add_node("sentiment_aggregator", sentiment_aggregator)
graph_builder.add_node("sentiment_evaluator", sentiment_evaluator)

# Edges
graph_builder.add_edge(START, "data_retrieval")

graph_builder.add_conditional_edges(
    "data_retrieval",
    data_retrieval_router,
    ["financial_analysis_agent", "market_trends_agent", "risk_assessment_agent", END],
)

graph_builder.add_edge("financial_analysis_agent", "sentiment_aggregator")
graph_builder.add_edge("market_trends_agent", "sentiment_aggregator")
graph_builder.add_edge("risk_assessment_agent", "sentiment_aggregator")
graph_builder.add_edge("sentiment_aggregator", "sentiment_evaluator")
graph_builder.add_conditional_edges(
    "sentiment_evaluator", sentiment_router, {"sentiment_aggregator": "sentiment_aggregator", END: END}
)

# Compile with cache
cache = InMemoryCache()
graph_workflow = graph_builder.compile(cache=cache)

# Uncomment to regenerate diagram when graph grows
# draw_architecture(graph_workflow)


# ── Input / Output Adapters ──────────────────────────────────────────────

def input(input_dict: dict) -> RealEstateResearchState:
    return RealEstateResearchState(
        address=input_dict["address"],
        purchase_price=input_dict.get("purchase_price"),
        down_payment_pct=input_dict.get("down_payment_pct", 20.0),
        loan_term_years=input_dict.get("loan_term_years", 30),
        interest_rate=input_dict.get("interest_rate"),
        estimated_rent=input_dict.get("estimated_rent"),
        time_horizon_years=input_dict.get("time_horizon_years", 10),
        data_retrieved=False,
        property_details="",
        market_trends="",
        financial_analysis="",
        risk_assessment="",
        combined_analysis="",
        compliant=False,
        feedback=None,
        revision_iteration_count=0,
    )


def output(state: dict | RealEstateResearchState) -> RealEstateResearchState:
    if isinstance(state, dict):
        state = RealEstateResearchState(**state)

    # During testing, allow partial results
    # Uncomment when ready for strict enforcement:
    if not state.data_retrieved:
        raise HTTPException(
            status_code=400,
            detail=f"Could not retrieve valid property data for address: {state.address}"
        )

    return state


# The chain — data retrieval → financial analysis + market trends (parallel)
research_chain_real_estate = RunnableLambda(input) | graph_workflow | RunnableLambda(output)