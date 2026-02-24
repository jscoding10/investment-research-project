from pydantic import BaseModel
from typing import Any
from enum import Enum

def format_analysis_output(output: Any) -> str:
    """
    Format agent output as readable markdown text.
    Handles:
    - Plain strings (e.g. from Groq Compound raw output)
    - Pydantic models (e.g. FinancialOutput, NewsSentimentOutput)
    """
    lines = []

    # Case 1: raw markdown string from LLM (most common for Compound agents)
    if isinstance(output, str):
        return output.strip()

    # Case 2: Pydantic model
    if isinstance(output, BaseModel):
        data = output.model_dump()

        # Main recommendation / sentiment / trend
        main_field = None
        for field in ["recommendation", "sentiment", "trend", "overall_risk", "investment_takeaway"]:
            if field in data:
                main_field = data[field]
                if isinstance(main_field, Enum):
                    main_field = main_field.value
                lines.append(f"**{main_field}**")
                break

        lines.append("")

        # Key points / facts / developments / risks
        key_list_fields = [
            "key_points", "key_facts", "key_risks", "key_comps",
            "recent_developments", "key_findings"
        ]
        for field in key_list_fields:
            items = data.get(field, [])
            if items:
                for item in items:
                    if isinstance(item, dict):  
                        point = item.get("point", "")
                        source = item.get("source", "")
                        date = item.get("date", "")
                        citation = f" [{source}"
                        if date:
                            citation += f", {date}"
                        citation += "]" if source else ""
                        lines.append(f"* {point}{citation}")
                    else:  # plain string
                        lines.append(f"* {item}")
                break  

        lines.append("")

        # Confidence
        if "confidence" in data:
            conf = data["confidence"]
            if isinstance(conf, Enum):
                conf = conf.value
            lines.append(f"**Confidence:** {conf}")

        return "\n".join(lines)

    # Fallback: anything else
    return str(output)