import os
import dotenv
from langchain_groq import ChatGroq

from agents.evaluation.prompt import sentiment_evaluator_prompt
from agents.shared.llm_models import LLM_MODELS
from models.agent import AggregatorFeedback

dotenv.load_dotenv()


def evaluate_aggregated_sentement(sentiment: str):

    prompt = f"Evaluate this sentiment for criteria compliance: {sentiment}"

    prompt += (
        f"Use these criteria as the evaluation target: {sentiment_evaluator_prompt}"
    )

    model = LLM_MODELS["groq-llama"]
    api_key = os.getenv("GROQ_API_KEY_3")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found! "
            "Make sure you have a .env file with GROQ_API_KEY_3=your_real_key_here"
            )  
    llm = ChatGroq(model = model, temperature = 0.0, groq_api_key = api_key).with_structured_output(
        schema=AggregatorFeedback
    )
    result = llm.invoke(prompt)

    if result is None:
        return {
            "compliant": True,
            "feedback": "Evaluation unavailable due to API error.",
        }

    return {"compliant": result.compliant, "feedback": result.feedback}