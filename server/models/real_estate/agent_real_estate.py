from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

# ============================================================================
# Shared Enums
# ============================================================================

class Confidence(str, Enum):
    """Confidence level for any agent analysis."""

    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class FinancialRecommendation(str, Enum):
    """Financial analysis recommendation."""

    STRONG = "Strong"
    MARGINAL = "Marginal"
    NEGATIVE = "Negative"


class MarketSentiment(str, Enum):
    """Market/investment takeaway sentiment."""

    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


class RiskLevel(str, Enum):
    """Overall risk level."""

    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"


class AggregatorRecommendation(str, Enum):
    """Final aggregator recommendation."""

    STRONG_BUY = "STRONG BUY"
    HOLD = "HOLD"
    AVOID = "AVOID"


# ============================================================================
# Shared Models
# ============================================================================


class KeyPointWithCitation(BaseModel):
    """A single key point with optional source citation — perfect for web-grounded sections."""

    point: str = Field(description="The key insight or fact")
    source: Optional[str] = Field(
        default=None, description="Source name (Zillow, Redfin, local news, etc.)"
    )
    date: Optional[str] = Field(
        default=None, description="Date of the source (YYYY-MM-DD or Month YYYY)"
    )


# ============================================================================
# Agent Output Models
# ============================================================================

class MarketTrendsOutput(BaseModel):
    """Structured output for market_trends_agent."""

    market_summary: str = Field(description="Single sentence Zillow + news summary")
    key_metrics: str = Field(description="The exact KEY METRICS block as string (or you can split later)")
    recent_developments: List[KeyPointWithCitation] = Field(
        description="3-4 recent developments with citations"
    )
    investment_takeaway: str = Field(
        description="Full investment takeaway paragraph (includes BULLISH/BEARISH/NEUTRAL)"
    )
    confidence: Confidence = Field(description="Confidence level")


class FinancialOutput(BaseModel):
    """Structured output for get_financial_analysis."""

    recommendation: FinancialRecommendation = Field(
        description="Strong / Marginal / Negative"
    )
    cap_rate: Optional[float] = Field(default=None, description="Cap rate %")
    cash_on_cash: Optional[float] = Field(default=None, description="Cash-on-cash return %")
    key_points: List[str] = Field(
        description="3-6 full sentences of quantitative analysis (per prompt rules)"
    )
    confidence: Confidence = Field(description="Confidence level")


class RiskOutput(BaseModel):
    """Structured output for get_risk_assessment."""

    risk_summary: str = Field(description="RISK & LIVABILITY SUMMARY (1-2 sentences)")
    key_factors: List[str] = Field(
        description="Crime grades and school ratings (the KEY FACTORS block)"
    )
    key_risks: List[KeyPointWithCitation] = Field(  # renamed from key_risks for clarity but kept field name for formatting
        description="Recent signals / risks with citations (matches formatting_real_estate)"
    )
    overall_risk: RiskLevel = Field(description="LOW / MODERATE / HIGH")
    confidence: Confidence = Field(description="Confidence level")

# ============================================================================
# Evaluator Models
# ============================================================================


class AggregatorFeedback(BaseModel):
    """Feedback from sentiment_evaluator (exactly matches your crypto version)."""

    compliant: bool = Field(
        description="Whether the aggregated analysis complies with the criteria"
    )
    feedback: str = Field(
        description="Specific feedback on what's missing or needs improvement. "
        "Empty string if compliant."
    )