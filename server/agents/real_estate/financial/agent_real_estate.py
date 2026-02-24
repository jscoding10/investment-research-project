import os
import json
import dotenv

from agents.shared.real_estate.agent_utils_real_estate import run_agent_with_tools  
from agents.shared.real_estate.llm_models_real_estate import LLM_MODELS, get_groq_llm
from agents.real_estate.financial.prompt_real_estate import financial_analysis_prompt
from agents.real_estate.financial.tools_real_estate import get_financial_metrics_tool
from models.real_estate.agent_real_estate import FinancialOutput

from util.logger import get_logger

logger = get_logger(__name__)

dotenv.load_dotenv()

def get_financial_analysis(state):
    if not state.data_retrieved:
        raise ValueError("Data retrieval must complete before financial analysis")

    prompt = financial_analysis_prompt.format(
        address=state.address,
        purchase_price=state.purchase_price,
        down_payment_pct=state.down_payment_pct,
        loan_term_years=state.loan_term_years,
        interest_rate=state.interest_rate,
        estimated_rent=state.estimated_rent,
        time_horizon_years=state.time_horizon_years,
        zestimate=state.zestimate,
        rent_estimate=state.rent_estimate,
        tax_annual=state.tax_annual,
        hoa_monthly=state.hoa_monthly,
    )

    tools = [get_financial_metrics_tool]
    model = LLM_MODELS["groq-llama"]
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found!")

    llm = get_groq_llm(model=model, api_key=api_key, temperature=0.0)
    
    result = run_agent_with_tools(llm, prompt, tools, FinancialOutput)
    return result