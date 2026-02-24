from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class Confidence(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class KeyPointWithCitation(BaseModel):
    point: str = Field(...)
    source: str = Field(...)
    date: Optional[str] = None

class PropertyOutput(BaseModel):
    summary: str
    key_facts: List[str]
    confidence: Confidence

class MarketTrendsOutput(BaseModel):
    market_summary: str
    key_metrics: str
    recent_developments: str
    investment_takeaway: str
    confidence: str

class FinancialOutput(BaseModel):
    recommendation: str = Field(..., description="Strong Cash Flow / Marginal / Negative")
    cap_rate: Optional[float]
    cash_on_cash: Optional[float]
    key_points: List[str]
    confidence: Confidence

class RiskOutput(BaseModel):
    overall_risk: str = Field(..., description="Low / Medium / High")
    key_risks: List[str]
    confidence: Confidence

class CompsOutput(BaseModel):
    valuation_range: str
    key_comps: List[str]
    confidence: Confidence

class AggregatorFeedback(BaseModel):
    compliant: bool = Field(description="Whether the aggregated analysis complies with the criteria")
    feedback: str = Field(description="Specific feedback on what's missing or needs improvement")