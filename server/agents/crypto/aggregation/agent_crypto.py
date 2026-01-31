import os
import dotenv

from agents.crypto.aggregation.prompt_crypto import research_aggregation_prompt
from models.crypto.state_crypto import CryptoResearchState
from agents.shared.crypto.agent_utils_crypto import run_agent_with_tools
from agents.shared.crypto.llm_models_crypto import LLM_MODELS, get_groq_llm


dotenv.load_dotenv()


def get_aggregated_sentiment(state: CryptoResearchState):

    if state.feedback:
        prompt = f"Your original response: {state.combined_sentiment}. Revise your response based on this feedback: {state.feedback}"
    else:
        prompt = f"{research_aggregation_prompt}\n\nAggregate the following crypto research:\n\n"
        prompt += f"Ticker: {state.ticker}\n"
        prompt += f"Trade Duration: {state.trade_duration.value}\n"
        prompt += f"Trade Direction: {state.trade_direction.value}"
        prompt += f"Technical Analysis:\n{state.technical_sentiment}\n\n"
        prompt += f"Macro Analysis:\n{state.macro_sentiment}\n\n"
        prompt += f"Peer Analysis:\n{state.peer_sentiment}\n\n"
        prompt += f"News Analysis:\n{state.news_sentiment}\n\n"

    model = LLM_MODELS["groq-llama"]

    api_key = os.getenv("GROQ_API_KEY_3")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found! "
            "Make sure you have a .env file with GROQ_API_KEY_3=your_real_key_here"
            )  

    llm = get_groq_llm(model = model, api_key = api_key, temperature = 0.2)

    result = run_agent_with_tools(llm, prompt)

    return result