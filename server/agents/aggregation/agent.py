import dotenv
from langchain_groq import ChatGroq

from agents.aggregation.prompt import research_aggregation_prompt
from models.state import EquityResearchState
from agents.shared.agent_utils import run_agent_with_tools
from agents.shared.llm_models import LLM_MODELS


dotenv.load_dotenv()


def get_aggregated_sentiment(state: EquityResearchState):

    if state.feedback:
        prompt = f"Your original response: {state.combined_sentiment}. Revise your response based on this feedback: {state.feedback}"
    else:
        prompt = f"{research_aggregation_prompt}\n\nAggregate the following equity research:\n\n"
        prompt += f"Ticker: {state.ticker}\n"
        prompt += f"Trade Duration: {state.trade_duration.value}\n"
        prompt += f"Trade Direction: {state.trade_direction.value}"
        prompt += f"Fundamental Analysis:\n{state.fundamental_sentiment}\n\n"
        prompt += f"Technical Analysis:\n{state.technical_sentiment}\n\n"
        prompt += f"Macro Analysis:\n{state.macro_sentiment}\n\n"
        prompt += f"Peer Analysis:\n{state.peer_sentiment}\n\n"
        prompt += f"Industry Analysis:\n{state.industry_sentiment}\n\n"
        prompt += f"News Analysis:\n{state.news_sentiment}\n\n"

    model = LLM_MODELS["groq-llama"]
    # Slight creativity allowed for synthesis & narrative
    # api_key auto-loaded from .env → GROQ_API_KEY
    llm = ChatGroq(model=model, temperature=0.2)
    result = run_agent_with_tools(llm, prompt)

    return result