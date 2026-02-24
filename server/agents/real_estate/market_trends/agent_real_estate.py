# import os
# import dotenv
# from datetime import datetime, timedelta

# from langchain_core.messages import HumanMessage

# from agents.shared.real_estate.llm_models_real_estate import LLM_MODELS, get_groq_compound_llm
# from agents.real_estate.market_trends.prompt_real_estate import market_trends_prompt

# from util.logger import get_logger

# logger = get_logger(__name__)

# dotenv.load_dotenv()


# def get_market_trends(state):
#     """
#     Market trends analysis via Groq Compound (built-in web search).
#     Grounds in Zillow data + real-time news. No custom tools required.
#     """
#     if not state.data_retrieved:
#         raise ValueError("Data retrieval must complete before market trends analysis")

#     # Build Zillow context
#     market_context = f"""
#     Zillow Market Overview for {state.city or 'N/A'}, {state.state or 'N/A'} {state.zip_code or ''}:
#     - Typical home value (ZHVI): ${getattr(state, 'market_typical_value', 0):,.0f}
#     - Year-over-year change: {getattr(state, 'market_yoy_change_pct', 0):+.1f}%
#     - For-sale inventory: {getattr(state, 'market_inventory', 0):,} homes
#     - Median days to pending: {getattr(state, 'market_days_pending', 0)} days
#     - Sale-to-list ratio: {getattr(state, 'market_sale_to_list', 0):.3f}
#     - Description: {getattr(state, 'market_description', 'N/A')}
#     """

#     prompt = market_trends_prompt.format(
#         location=f"ZIP {state.zip_code or ''}, {state.city or ''}, {state.state or ''}".strip(),
#         market_context=market_context.strip(),
#         market_typical_value=getattr(state, 'market_typical_value', 0),
#         market_yoy_change_pct=getattr(state, 'market_yoy_change_pct', 0),
#         market_inventory=getattr(state, 'market_inventory', 0),
#         market_days_pending=getattr(state, 'market_days_pending', 0),
#         market_sale_to_list=getattr(state, 'market_sale_to_list', 0),
#     )

#     # Groq Compound — built-in web search + reasoning, no tools list
#     model = LLM_MODELS["groq-compound-mini"]  # Fastest for single search + synthesis
#     api_key = os.getenv("GROQ_API_KEY_2")
#     if not api_key:
#         raise ValueError("GROQ_API_KEY_2 not found!")

#     llm = get_groq_compound_llm(
#         model=model,
#         api_key=api_key,
#         max_tokens=950,
#         temperature=0.0
#     )

#     logger.info(f"Starting market trends (Compound) for {state.address} (ZIP: {state.zip_code})")
#     result = llm.invoke([HumanMessage(content=prompt)])
#     logger.info(f"Market trends complete for {state.address}")

#     return result.content.strip()

# import os
# import dotenv
# from datetime import datetime, timedelta

# from langchain_core.messages import HumanMessage

# from agents.shared.real_estate.llm_models_real_estate import LLM_MODELS, get_groq_compound_llm
# from agents.real_estate.market_trends.prompt_real_estate import market_trends_prompt

# from util.logger import get_logger

# logger = get_logger(__name__)

# dotenv.load_dotenv()


# def nf(v, fmt: str = "", na: str = "N/A") -> str:
#     """Safe number formatter that returns 'N/A' on None or formatting errors.
    
#     IMPORTANT: Only call this when expect a number."""
#     if v is None:
#         return na
#     try:
#         return f"{v:{fmt}}"
#     except (ValueError, TypeError):
#         return na


# def get_market_trends(state):
#     """
#     Market trends analysis via Groq Compound (built-in web search).
#     Grounds in Zillow data + real-time news.
#     """
#     try:
#         if not state.data_retrieved:
#             raise ValueError("Data retrieval must complete before market trends analysis")

#         # ── Determine whether have usable Zillow market data ────────────────────────────────────────────────
#         has_market_data = state.zillow_market_raw is not None

#         # ── Build context block ──────────────────────────────────────────────────
#         if has_market_data:
#             market_context = f"""
#             Zillow Market Overview for {state.city or 'N/A'}, {state.state or 'N/A'} {state.zip_code or ''}:
#             - Typical home value (ZHVI): ${nf(state.market_typical_value, ',.0f')}
#             - Year-over-year change: {nf(state.market_yoy_change_pct, '+.1f')}%
#             - For-sale inventory: {nf(state.market_inventory, ',')} homes
#             - Median days to pending: {nf(state.market_days_pending)} days
#             - Sale-to-list ratio: {nf(state.market_sale_to_list, '.3f')}
#             - Description: {getattr(state, 'market_description', 'N/A')}
#             """

#             prompt_values = {
#                     'market_typical_value': nf(state.market_typical_value, ',.0f'),
#                     'market_yoy_change_pct': nf(state.market_yoy_change_pct, '+.1f'),
#                     'market_inventory': nf(state.market_inventory, ','),
#                     'market_days_pending': nf(state.market_days_pending),
#                     'market_sale_to_list': nf(state.market_sale_to_list, '.3f'),
#                 }
        
#         else:
#             # IMPORTANT: Keep this message very clear so the LLM does NOT hallucinate numbers
#             market_context = f"""
#             No Zillow market data available for {state.zip_code or 'N/A'}.
#             Rely on recent news only.
#             """.strip()

#             # Use 'N/A' consistently so prompt template stays uniform
#             prompt_values = {
#                 'market_typical_value': 'N/A',
#                 'market_yoy_change_pct': 'N/A',
#                 'market_inventory': 'N/A',
#                 'market_days_pending': 'N/A',
#                 'market_sale_to_list': 'N/A',
#             }
        
#         # ── Build final prompt ────────────────────────────────────────────────
#         prompt = market_trends_prompt.format(
#             location=f"ZIP {state.zip_code or ''}, {state.city or ''}, {state.state or ''}".strip(),
#             market_context=market_context,
#             **prompt_values
#         )

#         # Groq Compound — built-in web search + reasoning, no tools list
#         model = LLM_MODELS["groq-compound-mini"]  # Fastest for single search + synthesis
#         api_key = os.getenv("GROQ_API_KEY")
#         if not api_key:
#             raise ValueError("GROQ_API_KEY_2 not found!")

#         llm = get_groq_compound_llm(
#             model=model,
#             api_key=api_key,
#             max_tokens=950,
#             temperature=0.0
#         )

#         logger.info(f"Starting market trends (Compound) for {state.address} (ZIP: {state.zip_code})")
#         result = llm.invoke([HumanMessage(content=prompt)])
#         logger.info(f"Market trends complete for {state.address}")

#         return result.content.strip()
#     except Exception as e:
#         logger.error(f"Error in get_market_trends: {e}", exc_info=True)
#         return f"Error executing agent: {str(e)}"
    


import os
import dotenv

from langchain_core.messages import HumanMessage

from agents.shared.real_estate.llm_models_real_estate import LLM_MODELS, get_groq_compound_llm
from agents.real_estate.market_trends.prompt_real_estate import market_trends_prompt

from util.logger import get_logger

logger = get_logger(__name__)

dotenv.load_dotenv()


def nf(v, fmt: str = "", na: str = "N/A") -> str:
    """Safe formatter — only for numeric fields when has_market_data=True."""
    if v is None:
        return na
    try:
        return f"{v:{fmt}}"
    except (ValueError, TypeError):
        return na


def get_market_trends(state):
    """
    Market trends analysis via Groq Compound (built-in web search).
    """
    try:
        if not state.data_retrieved:
            raise ValueError("Data retrieval must complete before market trends analysis")

        has_market_data = state.zillow_market_raw is not None

        # ── Build prompt context ─────────────────────
        if has_market_data:
            market_context = (
                f"{state.city or 'N/A'}, {state.state or 'N/A'} {state.zip_code or ''}: "
                f"ZHVI ${nf(state.market_typical_value, ',.0f')} "
                f"({nf(state.market_yoy_change_pct, '+.1f')}% YoY) | "
                f"Inventory {nf(state.market_inventory, ',')} homes | "
                f"Days pending {nf(state.market_days_pending)} | "
                f"Sale/list {nf(state.market_sale_to_list, '.3f')}"
            )
            prompt_values = {
                'market_typical_value': nf(state.market_typical_value, ',.0f'),
                'market_yoy_change_pct': nf(state.market_yoy_change_pct, '+.1f'),
                'market_inventory': nf(state.market_inventory, ','),
                'market_days_pending': nf(state.market_days_pending),
                'market_sale_to_list': nf(state.market_sale_to_list, '.3f'),
            }
        else:
            market_context = f"No Zillow data for {state.zip_code or 'N/A'}. Use recent news only."
            prompt_values = {'market_typical_value': '', 'market_yoy_change_pct': '', 'market_inventory': '', 'market_days_pending': '', 'market_sale_to_list': ''}

        # ── Build prompt ───────────────────────────────────────────────────────
        prompt = market_trends_prompt.format(
            location=f"ZIP {state.zip_code or ''}, {state.city or ''}, {state.state or ''}".strip(),
            market_context=market_context,
            **prompt_values
        )

        model = LLM_MODELS["groq-compound-mini"]  
        api_key = os.getenv("GROQ_API_KEY_2")
        if not api_key:
            raise ValueError("GROQ_API_KEY_2 not found!")

        llm = get_groq_compound_llm(
            model=model,
            api_key=api_key,
            max_tokens=600,      
            temperature=0.0
        )

        logger.info(f"Starting market trends for {state.address} (ZIP: {state.zip_code})")
        result = llm.invoke([HumanMessage(content=prompt)])
        logger.info(f"Market trends complete for {state.address}")

        return result.content.strip()

    except Exception as e:
        logger.error(f"Error in get_market_trends for {state.address}: {e}", exc_info=True)
        return f"Error executing agent: {str(e)}"