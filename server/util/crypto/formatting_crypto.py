from pydantic import BaseModel

def format_sentiment_output(output: BaseModel) -> str:
    """Format a sentiment output model as readable text."""
    lines = []
    data = output.model_dump()

    # Get the main sentiment/valuation field
    if "sentiment" in data:
        sentiment_value = data['sentiment'].value if hasattr(data['sentiment'], 'value') else data['sentiment']
        lines.append(f"**{sentiment_value}**")
    elif "valuation" in data:
        valuation_value = data['valuation'].value if hasattr(data['valuation'], 'value') else data['valuation']
        lines.append(f"**{valuation_value}**")

    lines.append("")

    # Format key points (standard agents)
    for kp in data.get("key_points", []):
        if isinstance(kp, dict):
            # KeyPointWithCitation
            lines.append(f"* {kp['point']} [{kp['source']}, {kp['date']}]")
        else:
            # Simple string key point
            lines.append(f"* {kp}")

    lines.append("")

    # Format confidence
    if "confidence" in data:
        confidence_value = data['confidence'].value if hasattr(data['confidence'], 'value') else data['confidence']
        lines.append("")
        lines.append(f"**Confidence:** {confidence_value}")

    return "\n".join(lines)