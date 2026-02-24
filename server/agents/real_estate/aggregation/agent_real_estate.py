import os
import dotenv

from agents.real_estate.aggregation.prompt_real_estate import research_aggregation_prompt
from models.real_estate.state_real_estate import RealEstateResearchState
from agents.shared.real_estate.agent_utils_real_estate import run_agent_with_tools
from agents.shared.real_estate.llm_models_real_estate import LLM_MODELS, get_groq_llm


dotenv.load_dotenv()


def get_aggregated_analysis(state: RealEstateResearchState):

    if state.feedback:
        prompt = f"Your original response: {state.combined_analysis}. Revise your response based on this feedback: {state.feedback}"
    else:
        prompt = f"{research_aggregation_prompt}\n\nAggregate the following real estate research:\n\n"
        prompt += f"Address: {state.address}\n"
        prompt += f"Financial Analysis:\n{state.financial_analysis}\n\n"
        prompt += f"Market Trends:\n{state.market_trends}\n\n"
        prompt += f"Risk Assessment:\n{state.risk_assessment}\n\n"

    model = LLM_MODELS["groq-llama"]

    api_key = os.getenv("GROQ_API_KEY_3")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY_3 not found! "
            "Make sure you have a .env file with GROQ_API_KEY_3=your_real_key_here"
            )  

    llm = get_groq_llm(model = model, api_key = api_key, temperature = 0.2)

    result = run_agent_with_tools(llm, prompt)

    return result