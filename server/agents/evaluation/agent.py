import os
import dotenv

from agents.evaluation.prompt import sentiment_evaluator_prompt
from agents.shared.llm_models import LLM_MODELS, get_groq_llm
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
    base_llm = get_groq_llm(model = model, api_key = api_key, temperature = 0.0)

    llm = base_llm.with_structured_output(schema = AggregatorFeedback)
    result = llm.invoke(prompt)

    if result is None:
        return {
            "compliant": True,
            "feedback": "Evaluation unavailable due to API error.",
        }

    return {"compliant": result.compliant, "feedback": result.feedback}