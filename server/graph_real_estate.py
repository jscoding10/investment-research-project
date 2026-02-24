# from langchain_core.runnables import RunnableLambda
# from langgraph.graph import END, StateGraph, START
# from langgraph.cache.memory import InMemoryCache
# from dotenv import load_dotenv
# from fastapi import HTTPException

# from agents.real_estate.evaluation.agent_real_estate import evaluate_aggregated_analysis
# from agents.real_estate.aggregation.agent_real_estate import get_aggregated_analysis
# from agents.real_estate.property.agent_real_estate import get_property_details
# from agents.real_estate.market.agent_real_estate import get_market_trends
# from agents.real_estate.financial.agent_real_estate import get_financial_analysis
# from agents.real_estate.data_retrieval.agent_real_estate import data_retrieval_agent

# from util.logger import get_logger
# from models.real_estate.state_real_estate import RealEstateResearchState
# from util.real_estate.cache_real_estate import create_cache_policy
# from util.real_estate.formatting_real_estate import format_analysis_output
# from util.diagrams import draw_architecture

# load_dotenv()
# logger = get_logger(__name__)


# # ── Nodes ────────────────────────────────────────────────────────────────

# def data_retrieval_node(state: RealEstateResearchState) -> dict:
#     """Fetch core property data from external APIs (Zillow, RentCast, etc.)"""
#     logger.info(f"Starting data retrieval for {state.address}")
#     try:
#         result = data_retrieval_agent(state)  # assuming this returns dict with data_retrieved, zpid, etc.
#         logger.info(f"Data retrieval complete for {state.address}")
#         return result
#     except Exception as e:
#         logger.error(f"Data retrieval failed for {state.address}: {e}", exc_info=True)
#         return {"data_retrieved": False}


# def data_retrieval_router(state: RealEstateResearchState):
#     """Route to research agents only if core data was successfully retrieved"""
#     if state.data_retrieved:
#         return [
#             "property_details_agent",
#             "market_trends_agent",
#             "financial_analysis_agent",
#         ]
#     else:
#         return END


# def property_details_agent(state: RealEstateResearchState) -> dict:
#     """Generate structured property details summary"""
#     logger.info(f"Starting property details for {state.address}")
#     try:
#         details = get_property_details(address=state.address)
#         logger.info(f"Completed property details for {state.address}")
#         return {"property_details": format_analysis_output(details)}
#     except Exception as e:
#         logger.error(f"Property details failed: {e}", exc_info=True)
#         return {"property_details": "Analysis unavailable due to data retrieval error."}


# def market_trends_agent(state: RealEstateResearchState) -> dict:
#     """Generate market trends and neighborhood/context analysis"""
#     logger.info(f"Starting market trends for {state.address}")
#     try:
#         trends = get_market_trends(address=state.address)
#         logger.info(f"Completed market trends for {state.address}")
#         return {"market_trends": format_analysis_output(trends)}
#     except Exception as e:
#         logger.error(f"Market trends failed: {e}", exc_info=True)
#         return {"market_trends": "Analysis unavailable due to data retrieval error."}


# def financial_analysis_agent(state: RealEstateResearchState) -> dict:
#     """Generate financial/investment analysis (cap rate, cash flow, ROI, etc.)"""
#     logger.info(f"Starting financial analysis for {state.address}")
#     try:
#         analysis = get_financial_analysis(state)  # assumes it can read purchase_price, rent, etc. from state
#         logger.info(f"Completed financial analysis for {state.address}")
#         return {"financial_analysis": format_analysis_output(analysis)}
#     except Exception as e:
#         logger.error(f"Financial analysis failed: {e}", exc_info=True)
#         return {"financial_analysis": "Analysis unavailable due to data retrieval error."}


# def analysis_aggregator(state: RealEstateResearchState) -> dict:
#     """Synthesize all research into a cohesive investment analysis"""
#     logger.info(f"Starting analysis aggregation for {state.address}")
#     try:
#         combined = get_aggregated_analysis(state)
#         logger.info(f"Completed aggregation for {state.address}")
#         return {"combined_analysis": combined}
#     except Exception as e:
#         logger.error(f"Aggregation failed: {e}", exc_info=True)
#         return {
#             "combined_analysis": (
#                 "**Conclusion:** Unable to fully synthesize analysis due to an internal error. "
#                 "Please review individual components for partial insights."
#             )
#         }


# def analysis_evaluator(state: RealEstateResearchState) -> dict:
#     """Critique / score the aggregated analysis for quality & completeness"""
#     logger.info("Starting analysis evaluation")
#     try:
#         evaluation = evaluate_aggregated_analysis(analysis=state.combined_analysis)
#         logger.info("Completed evaluation")
#         evaluation["revision_iteration_count"] = state.revision_iteration_count + 1
#         return evaluation
#     except Exception as e:
#         logger.error(f"Evaluation failed: {e}", exc_info=True)
#         return {
#             "compliant": True,
#             "feedback": "Evaluation skipped due to internal error.",
#             "revision_iteration_count": state.revision_iteration_count + 1,
#         }


# def analysis_router(state: RealEstateResearchState):
#     """Decide whether to accept output or loop back to aggregator"""
#     if state.compliant:
#         return "Compliant"
#     if state.revision_iteration_count > 2:
#         return "Compliant"  # prevent infinite loops
#     return "Noncompliant"


# # ── Graph Definition ─────────────────────────────────────────────────────

# graph_builder = StateGraph(RealEstateResearchState)

# # Nodes
# graph_builder.add_node("data_retrieval", data_retrieval_node)
# graph_builder.add_node("property_details_agent", property_details_agent)
# graph_builder.add_node("market_trends_agent", market_trends_agent)
# graph_builder.add_node("financial_analysis_agent", financial_analysis_agent)
# graph_builder.add_node("aggregator", analysis_aggregator)
# graph_builder.add_node("evaluator", analysis_evaluator)

# # Edges
# graph_builder.add_edge(START, "data_retrieval")

# graph_builder.add_conditional_edges(
#     "data_retrieval",
#     data_retrieval_router,
#     ["property_details_agent", "market_trends_agent", "financial_analysis_agent", END],
# )

# graph_builder.add_edge("property_details_agent", "aggregator")
# graph_builder.add_edge("market_trends_agent", "aggregator")
# graph_builder.add_edge("financial_analysis_agent", "aggregator")

# graph_builder.add_edge("aggregator", "evaluator")

# graph_builder.add_conditional_edges(
#     "evaluator",
#     analysis_router,
#     {"Compliant": END, "Noncompliant": "aggregator"},
# )

# # Compile with cache
# cache = InMemoryCache()
# graph_workflow = graph_builder.compile(cache=cache)

# # Uncomment to update diagram
# # draw_architecture(graph_workflow)


# # ── Input / Output Adapters ──────────────────────────────────────────────

# def input(input_dict: dict) -> RealEstateResearchState:
#     return RealEstateResearchState(
#         address=input_dict["address"],
#         purchase_price=input_dict.get("purchase_price"),
#         down_payment_pct=input_dict.get("down_payment_pct", 20.0),
#         loan_term_years=input_dict.get("loan_term_years", 30),
#         interest_rate=input_dict.get("interest_rate"),
#         estimated_rent=input_dict.get("estimated_rent"),
#         time_horizon_years=input_dict.get("time_horizon_years", 10),
#         # outputs
#         data_retrieved=False,
#         property_details="",
#         market_trends="",
#         financial_analysis="",
#         combined_analysis="",
#         compliant=False,
#         feedback=None,
#         revision_iteration_count=0,
#         zpid=None,
#         zillow_raw=None,
#         rentcast_raw=None,
#         # ... add any other fields your state model requires
#     )


# def output(state: dict | RealEstateResearchState) -> RealEstateResearchState:
#     if isinstance(state, dict):
#         state = RealEstateResearchState(**state)

#     if not state.data_retrieved:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Could not retrieve valid property data for address: {state.address}"
#         )
#     return state

###########################################################################################################
# # FastAPI / LangChain runnable chain
# research_chain_real_estate = RunnableLambda(input) | graph_workflow | RunnableLambda(output)

# from langchain_core.runnables import RunnableLambda
# from langgraph.graph import END, StateGraph, START
# from langgraph.cache.memory import InMemoryCache
# from dotenv import load_dotenv
# from fastapi import HTTPException

# from agents.real_estate.data_retrieval.agent_real_estate import data_retrieval_agent
# from agents.real_estate.financial.agent_real_estate import get_financial_analysis

# from util.logger import get_logger
# from models.real_estate.state_real_estate import RealEstateResearchState
# from util.real_estate.formatting_real_estate import format_analysis_output

# load_dotenv()
# logger = get_logger(__name__)


# # ── Nodes ────────────────────────────────────────────────────────────────

# def data_retrieval_node(state: RealEstateResearchState) -> dict:
#     """Fetch core property data from external APIs (Zillow, RentCast, etc.)"""
#     logger.info(f"Starting data retrieval for {state.address}")
#     try:
#         result = data_retrieval_agent(state)
#         logger.info(f"Data retrieval complete for {state.address} - ZPID: {state.zpid}")
#         return result
#     except Exception as e:
#         logger.error(f"Data retrieval failed for {state.address}: {e}", exc_info=True)
#         return {"data_retrieved": False}


# def data_retrieval_router(state: RealEstateResearchState):
#     """Route to financial agent only if core data was successfully retrieved"""
#     if state.data_retrieved:
#         return ["financial_analysis_agent"]
#     else:
#         return END


# def financial_analysis_agent(state: RealEstateResearchState) -> dict:
#     """Generate financial/investment analysis (cap rate, cash flow, ROI, etc.)"""
#     logger.info(f"Starting financial analysis for {state.address}")
#     try:
#         analysis = get_financial_analysis(state)
#         logger.info(f"Completed financial analysis for {state.address}")
#         return {"financial_analysis": format_analysis_output(analysis)}
#     except Exception as e:
#         logger.error(f"Financial analysis failed: {e}", exc_info=True)
#         return {"financial_analysis": "Analysis unavailable due to data retrieval error."}


# # ── For now everything below financial is commented out ──────────────────

# """
# def property_details_agent(state: RealEstateResearchState) -> dict:
#     logger.info(f"Starting property details for {state.address}")
#     try:
#         details = get_property_details(address=state.address)
#         logger.info(f"Completed property details for {state.address}")
#         return {"property_details": format_analysis_output(details)}
#     except Exception as e:
#         logger.error(f"Property details failed: {e}", exc_info=True)
#         return {"property_details": "Analysis unavailable due to data retrieval error."}


# def market_trends_agent(state: RealEstateResearchState) -> dict:
#     logger.info(f"Starting market trends for {state.address}")
#     try:
#         trends = get_market_trends(address=state.address)
#         logger.info(f"Completed market trends for {state.address}")
#         return {"market_trends": format_analysis_output(trends)}
#     except Exception as e:
#         logger.error(f"Market trends failed: {e}", exc_info=True)
#         return {"market_trends": "Analysis unavailable due to data retrieval error."}


# def analysis_aggregator(state: RealEstateResearchState) -> dict:
#     logger.info(f"Starting analysis aggregation for {state.address}")
#     try:
#         combined = get_aggregated_analysis(state)
#         logger.info(f"Completed aggregation for {state.address}")
#         return {"combined_analysis": combined}
#     except Exception as e:
#         logger.error(f"Aggregation failed: {e}", exc_info=True)
#         return {
#             "combined_analysis": (
#                 "**Conclusion:** Unable to fully synthesize analysis due to an internal error. "
#                 "Please review individual components for partial insights."
#             )
#         }


# def analysis_evaluator(state: RealEstateResearchState) -> dict:
#     logger.info("Starting analysis evaluation")
#     try:
#         evaluation = evaluate_aggregated_analysis(analysis=state.combined_analysis)
#         logger.info("Completed evaluation")
#         evaluation["revision_iteration_count"] = state.revision_iteration_count + 1
#         return evaluation
#     except Exception as e:
#         logger.error(f"Evaluation failed: {e}", exc_info=True)
#         return {
#             "compliant": True,
#             "feedback": "Evaluation skipped due to internal error.",
#             "revision_iteration_count": state.revision_iteration_count + 1,
#         }


# def analysis_router(state: RealEstateResearchState):
#     if state.compliant:
#         return "Compliant"
#     if state.revision_iteration_count > 2:
#         return "Compliant"
#     return "Noncompliant"
# """


# # ── Graph Definition ─────────────────────────────────────────────────────

# graph_builder = StateGraph(RealEstateResearchState)

# # Active nodes
# graph_builder.add_node("data_retrieval", data_retrieval_node)
# graph_builder.add_node("financial_analysis_agent", financial_analysis_agent)

# # Edges
# graph_builder.add_edge(START, "data_retrieval")

# graph_builder.add_conditional_edges(
#     "data_retrieval",
#     data_retrieval_router,
#     ["financial_analysis_agent", END],
# )

# # Do NOT connect to aggregator yet — it's not added
# # graph_builder.add_edge("financial_analysis_agent", "aggregator")  # ← this was causing the crash

# # ── When ready to add aggregator, uncomment its node definition above,
# #    then uncomment this edge:
# # graph_builder.add_edge("financial_analysis_agent", "aggregator")

# # Compile with cache
# cache = InMemoryCache()
# graph_workflow = graph_builder.compile(cache=cache)

# # Uncomment to regenerate diagram when graph grows
# # draw_architecture(graph_workflow)


# # ── Input / Output Adapters ──────────────────────────────────────────────

# def input(input_dict: dict) -> RealEstateResearchState:
#     return RealEstateResearchState(
#         address=input_dict["address"],
#         purchase_price=input_dict.get("purchase_price"),
#         down_payment_pct=input_dict.get("down_payment_pct", 20.0),
#         loan_term_years=input_dict.get("loan_term_years", 30),
#         interest_rate=input_dict.get("interest_rate"),
#         estimated_rent=input_dict.get("estimated_rent"),
#         time_horizon_years=input_dict.get("time_horizon_years", 10),
#         # outputs / flags
#         data_retrieved=False,
#         property_details="",
#         market_trends="",
#         financial_analysis="",
#         combined_analysis="",
#         compliant=False,
#         feedback=None,
#         revision_iteration_count=0,
#         zpid=None,
#         # Added
#         zillow_raw=None,
#         # Added
#         rentcast_raw=None,
#         # Add homeowners

#         # Add tax 
#     )


# def output(state: dict | RealEstateResearchState) -> RealEstateResearchState:
#     if isinstance(state, dict):
#         state = RealEstateResearchState(**state)

#     # During testing, allow partial results
#     # Uncomment when ready for strict enforcement:
#     # if not state.data_retrieved:
#     #     raise HTTPException(
#     #         status_code=400,
#     #         detail=f"Could not retrieve valid property data for address: {state.address}"
#     #     )

#     return state


# # The chain — data retrieval → financial analysis only
# research_chain_real_estate = RunnableLambda(input) | graph_workflow | RunnableLambda(output)








# #############################################################################################
# from langchain_core.runnables import RunnableLambda
# from langgraph.graph import END, StateGraph, START
# from langgraph.cache.memory import InMemoryCache
# from dotenv import load_dotenv
# from fastapi import HTTPException

# from agents.real_estate.data_retrieval.agent_real_estate import data_retrieval_agent
# from agents.real_estate.financial.agent_real_estate import get_financial_analysis
# from agents.real_estate.market_trends.agent_real_estate import get_market_trends   # ← NEW import
# from agents.real_estate.risk.agent_real_estate import get_risk_assessment   # ← NEW import
# from agents.real_estate.aggregation.agent_real_estate import get_aggregated_analysis   # ← NEW import
# from agents.real_estate.evaluation.agent_real_estate import evaluate_aggregated_analysis   # ← NEW import

# from util.logger import get_logger
# from models.real_estate.state_real_estate import RealEstateResearchState
# from util.real_estate.formatting_real_estate import format_analysis_output

# load_dotenv()
# logger = get_logger(__name__)


# # ── Nodes ────────────────────────────────────────────────────────────────

# def data_retrieval_node(state: RealEstateResearchState) -> dict:
#     """Fetch core property data from external APIs (Zillow, RentCast, etc.)"""
#     logger.info(f"Starting data retrieval for {state.address}")
#     try:
#         result = data_retrieval_agent(state)
#         logger.info(f"Data retrieval complete for {state.address} - ZPID: {state.zpid}")
#         return result
#     except Exception as e:
#         logger.error(f"Data retrieval failed for {state.address}: {e}", exc_info=True)
#         return {"data_retrieved": False}


# def data_retrieval_router(state: RealEstateResearchState):
#     """Route to financial + market agents only if core data was successfully retrieved"""
#     if state.data_retrieved:
#         return ["financial_analysis_agent", "market_trends_agent", "risk_assessment_agent"]
#     else:
#         return END


# def financial_analysis_agent(state: RealEstateResearchState) -> dict:
#     """Generate financial/investment analysis (cap rate, cash flow, ROI, etc.)"""
#     logger.info(f"Starting financial analysis for {state.address}")
#     try:
#         analysis = get_financial_analysis(state)
#         logger.info(f"Completed financial analysis for {state.address}")
#         return {"financial_analysis": format_analysis_output(analysis)}
#     except Exception as e:
#         logger.error(f"Financial analysis failed: {e}", exc_info=True)
#         return {"financial_analysis": "Analysis unavailable due to data retrieval error."}


# def market_trends_agent(state: RealEstateResearchState) -> dict:
#     """Generate market trends analysis using Groq Compound + Zillow grounding"""
#     logger.info(f"Starting market trends for {state.address}")
#     try:
#         trends = get_market_trends(state)
#         logger.info(f"Completed market trends for {state.address}")
#         return {"market_trends": format_analysis_output(trends)}
#     except Exception as e:
#         logger.error(f"Market trends failed: {e}", exc_info=True)
#         return {"market_trends": "Analysis unavailable due to data retrieval error."}

# def risk_assessment_agent(state: RealEstateResearchState) -> dict:
#     """Generate risk/livability assessment (crime + schools + context)"""
#     logger.info(f"Starting risk assessment for {state.address}")
#     try:
#         risk = get_risk_assessment(state)
#         logger.info(f"Completed risk assessment for {state.address}")
#         return {"risk_assessment": format_analysis_output(risk)}
#     except Exception as e:
#         logger.error(f"Risk assessment failed: {e}", exc_info=True)
#         return {"risk_assessment": "Risk assessment unavailable due to data retrieval error."}


# def aggregator_node(state: RealEstateResearchState) -> dict:
#     """Synthesize financial, market trends, and risk analyses into cohesive thesis"""
#     logger.info(f"Starting analysis aggregation for {state.address}")
#     try:
#         aggregated = get_aggregated_analysis(state)
#         logger.info(f"Completed aggregation for {state.address}")
#         return {
#             "combined_analysis": aggregated,
#             "revision_iteration_count": state.revision_iteration_count
#         }
#     except Exception as e:
#         logger.error(f"Aggregation failed: {e}", exc_info=True)
#         return {
#             "combined_analysis": (
#                 "**Conclusion:** Unable to fully synthesize analysis due to an internal error. "
#                 "Please review individual components for partial insights."
#             ),
#             "revision_iteration_count": state.revision_iteration_count
#         }


# def evaluator_node(state: RealEstateResearchState) -> dict:
#     """Evaluate aggregated analysis and provide feedback if non-compliant"""
#     logger.info(f"Starting aggregated analysis evaluation for {state.address}")
#     try:
#         evaluation = evaluate_aggregated_analysis(state.combined_analysis)
#         logger.info(f"Completed evaluation for {state.address}")
#         return {
#             "compliant": evaluation["compliant"],
#             "feedback": evaluation["feedback"],
#             "revision_iteration_count": state.revision_iteration_count + 1
#         }
#     except Exception as e:
#         logger.error(f"Evaluation failed: {e}", exc_info=True)
#         return {
#             "compliant": True,  # fail open to avoid infinite loop
#             "feedback": "Evaluation skipped due to internal error.",
#             "revision_iteration_count": state.revision_iteration_count + 1
#         }

# def sentiment_aggregator(state: RealEstateResearchState) -> dict:
#     """LLM call to aggregate research findings and synthesize sentiment"""
#     logger.info(f"Starting sentiment aggregation for {state.address}")
#     try:
#         combined_sentiment = get_aggregated_analysis(state)
#         logger.info(f"Completed sentiment aggregation for {state.address}")
#         return {"combined_analysis": combined_sentiment}
#     except Exception as e:
#         logger.error(
#             f"Sentiment aggregation failed for {state.address}: {e}", exc_info=True
#         )
#         return {
#             "combined_analysis": (
#                 f"**Conclusion:** Unable to fully synthesize sentiment due to an internal error. "
#                 f"Please review individual research components for partial analysis."
#             )
#         }

# def sentiment_evaluator(state: RealEstateResearchState) -> dict:
#     """LLM call to evaluate sentiment aggregator output"""
#     logger.info("Starting sentiment evaluation")
#     try:
#         sentiment_evaluation = evaluate_aggregated_analysis(
#             analysis=state.combined_analysis
#         )
#         logger.info("Completed sentiment evaluation")
#         sentiment_evaluation["revision_iteration_count"] = (
#             state.revision_iteration_count + 1
#         )
#         return sentiment_evaluation
#     except Exception as e:
#         logger.error(f"Sentiment evaluation failed: {e}", exc_info=True)
#         # Mark as compliant to avoid infinite retry loops - log the failure
#         return {
#             "compliant": True,
#             "feedback": "Evaluation skipped due to internal error.",
#             "revision_iteration_count": state.revision_iteration_count + 1,
#         }

# def sentiment_router(state: RealEstateResearchState):
#     "Route back to aggregator or terminate based on evaluator feedback"
#     if state.compliant == True:
#         return END
#     elif state.revision_iteration_count > 2:
#         return END
#     else:
#         return "sentiment_aggregator"


# # ── Graph Definition ─────────────────────────────────────────────────────

# graph_builder = StateGraph(RealEstateResearchState)

# # Active nodes
# graph_builder.add_node("data_retrieval", data_retrieval_node)
# graph_builder.add_node("financial_analysis_agent", financial_analysis_agent)
# graph_builder.add_node("market_trends_agent", market_trends_agent)
# graph_builder.add_node("risk_assessment_agent", risk_assessment_agent)
# graph_builder.add_node("sentiment_aggregator", sentiment_aggregator)
# graph_builder.add_node("sentiment_evaluator", sentiment_evaluator)

# # Edges
# graph_builder.add_edge(START, "data_retrieval")

# graph_builder.add_conditional_edges(
#     "data_retrieval",
#     data_retrieval_router,
#     ["financial_analysis_agent", "market_trends_agent", "risk_assessment_agent", END],
# )

# # Connect both analysis branches to aggregator (uncomment when aggregator exists)
# # graph_builder.add_edge("financial_analysis_agent", "analysis_aggregator")
# # graph_builder.add_edge("market_trends_agent", "analysis_aggregator")

# # For now: end after both analyses (parallel branches terminate independently)
# graph_builder.add_edge("financial_analysis_agent", END)
# graph_builder.add_edge("market_trends_agent", END)
# graph_builder.add_edge("risk_assessment_agent", END)   # ← NEW edge

# # Compile with cache
# cache = InMemoryCache()
# graph_workflow = graph_builder.compile(cache=cache)

# # Uncomment to regenerate diagram when graph grows
# # draw_architecture(graph_workflow)


# # ── Input / Output Adapters ──────────────────────────────────────────────

# def input(input_dict: dict) -> RealEstateResearchState:
#     return RealEstateResearchState(
#         address=input_dict["address"],
#         purchase_price=input_dict.get("purchase_price"),
#         down_payment_pct=input_dict.get("down_payment_pct", 20.0),
#         loan_term_years=input_dict.get("loan_term_years", 30),
#         interest_rate=input_dict.get("interest_rate"),
#         estimated_rent=input_dict.get("estimated_rent"),
#         time_horizon_years=input_dict.get("time_horizon_years", 10),
#         # outputs / flags
#         data_retrieved=False,
#         property_details="",
#         market_trends="",
#         financial_analysis="",
#         risk_assessment="",
#         combined_analysis="",
#         compliant=False,
#         feedback=None,
#         revision_iteration_count=0,
#         zpid=None,
#         # Added
#         zillow_raw=None,
#         # Added
#         rentcast_raw=None,
#         # Add homeowners

#         # Add tax 
#     )


# def output(state: dict | RealEstateResearchState) -> RealEstateResearchState:
#     if isinstance(state, dict):
#         state = RealEstateResearchState(**state)

#     # During testing, allow partial results
#     # Uncomment when ready for strict enforcement:
#     # if not state.data_retrieved:
#     #     raise HTTPException(
#     #         status_code=400,
#     #         detail=f"Could not retrieve valid property data for address: {state.address}"
#     #     )

#     return state


# # The chain — data retrieval → financial analysis + market trends (parallel)
# research_chain_real_estate = RunnableLambda(input) | graph_workflow | RunnableLambda(output)
#############################################################################################
from langchain_core.runnables import RunnableLambda
from langgraph.graph import END, StateGraph, START
from langgraph.cache.memory import InMemoryCache
from dotenv import load_dotenv
from fastapi import HTTPException

from agents.real_estate.data_retrieval.agent_real_estate import data_retrieval_agent
from agents.real_estate.financial.agent_real_estate import get_financial_analysis
from agents.real_estate.market_trends.agent_real_estate import get_market_trends   # ← NEW import
from agents.real_estate.risk.agent_real_estate import get_risk_assessment   # ← NEW import
from agents.real_estate.aggregation.agent_real_estate import get_aggregated_analysis   # ← NEW import
from agents.real_estate.evaluation.agent_real_estate import evaluate_aggregated_analysis   # ← NEW import

from util.logger import get_logger
from models.real_estate.state_real_estate import RealEstateResearchState
from util.real_estate.formatting_real_estate import format_analysis_output

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
graph_builder.add_node("data_retrieval", data_retrieval_node)
graph_builder.add_node("financial_analysis_agent", financial_analysis_agent)
graph_builder.add_node("market_trends_agent", market_trends_agent)
graph_builder.add_node("risk_assessment_agent", risk_assessment_agent)
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
        # outputs / flags
        data_retrieved=False,
        property_details="",
        market_trends="",
        financial_analysis="",
        risk_assessment="",
        combined_analysis="",
        compliant=False,
        feedback=None,
        revision_iteration_count=0,
        zpid=None,
        # Added
        zillow_raw=None,
        # Added
        rentcast_raw=None,
        # Add homeowners

        # Add tax 
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