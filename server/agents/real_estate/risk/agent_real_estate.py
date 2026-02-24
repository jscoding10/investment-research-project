import os
from langchain_core.messages import HumanMessage

from agents.shared.real_estate.llm_models_real_estate import LLM_MODELS, get_groq_compound_llm
from agents.real_estate.risk.prompt_real_estate import risk_assessment_prompt

from util.logger import get_logger

logger = get_logger(__name__)


def nf(v, fmt: str = "", na: str = "N/A") -> str:
    """Safe number/string formatter — returns 'N/A' on None or formatting errors."""
    if v is None:
        return na
    try:
        return f"{v:{fmt}}"
    except (ValueError, TypeError):
        return na


def get_risk_assessment(state):
    """
    Risk & livability assessment combining crime grades, school ratings,
    and recent contextual news via Groq Compound (built-in search).

    Grounds analysis in already-extracted data from retrieval step.
    Treats missing data gracefully (no crash).
    """
    try:
        if not state.data_retrieved:
            raise ValueError("Data retrieval must complete before risk assessment")

        # ── Build grounded context from state ────────────────────────────────
        crime_str = "No crime data available."
        if state.crime_overall_grade:
            crime_str = (
                f"Overall: {state.crime_overall_grade}, "
                f"Violent: {nf(state.crime_violent_grade)}, "
                f"Property: {nf(state.crime_property_grade)}"
            )

        schools_str = "No school ratings available."
        school_lines = []
        if state.elementary_school_name:
            school_lines.append(
                f"Elementary: {state.elementary_school_name} "
                f"(rating {nf(state.elementary_school_rating)})"
            )
        if state.middle_school_name:
            school_lines.append(
                f"Middle: {state.middle_school_name} "
                f"(rating {nf(state.middle_school_rating)})"
            )
        if state.high_school_name:
            school_lines.append(
                f"High: {state.high_school_name} "
                f"(rating {nf(state.high_school_rating)})"
            )
        if school_lines:
            schools_str = "\n".join(school_lines)

        location = f"ZIP {state.zip_code or 'N/A'}, {state.city or ''}, {state.state or ''}".strip()

        # ── Pre-compute safe strings with fallbacks ───────────────────────────
        crime_overall  = state.crime_overall_grade  or "Data unavailable"
        crime_violent  = state.crime_violent_grade  or "N/A"
        crime_property = state.crime_property_grade or "N/A"

        elem_name   = state.elementary_school_name   or "N/A"
        elem_rating = nf(state.elementary_school_rating)
        mid_name    = state.middle_school_name       or "N/A"
        mid_rating  = nf(state.middle_school_rating)
        high_name   = state.high_school_name         or "N/A"
        high_rating = nf(state.high_school_rating)

        # ── Format prompt ─────────────────────────────────────────────────────
        prompt = risk_assessment_prompt.format(
            address=state.address,
            location=location,
            crime_context=crime_str,
            schools_context=schools_str,
            crime_overall_grade=crime_overall,
            crime_violent_grade=crime_violent,
            crime_property_grade=crime_property,
            elementary_school_name=elem_name,
            elementary_school_rating=elem_rating,
            middle_school_name=mid_name,
            middle_school_rating=mid_rating,
            high_school_name=high_name,
            high_school_rating=high_rating,
        )

        # ── Groq Compound (fast + search-capable) ─────────────────────────────
        model = LLM_MODELS["groq-compound-mini"]
        api_key = os.getenv("GROQ_API_KEY")  
        if not api_key:
            raise ValueError("GROQ_API_KEY not found!")

        llm = get_groq_compound_llm(
            model=model,
            api_key=api_key,
            max_tokens=750,
            temperature=0.0
        )

        logger.info(f"Starting risk assessment for {state.address} (ZIP: {state.zip_code or 'N/A'})")
        result = llm.invoke([HumanMessage(content=prompt)])
        logger.info(f"Risk assessment complete for {state.address}")

        return result.content.strip()

    except Exception as e:
        logger.error(f"Error in get_risk_assessment for {state.address}: {e}", exc_info=True)
        return f"Risk assessment unavailable: {str(e)}"