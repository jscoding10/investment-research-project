import os
import dotenv

from agents.real_estate.evaluation.prompt_real_estate import sentiment_evaluator_prompt
from agents.shared.real_estate.llm_models_real_estate import LLM_MODELS, get_groq_llm
from models.real_estate.agent_real_estate import AggregatorFeedback

dotenv.load_dotenv()


def evaluate_aggregated_analysis(analysis: str):

    prompt = f"Evaluate this analysis for criteria compliance: {analysis}"

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