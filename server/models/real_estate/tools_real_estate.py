from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class FinancialMetricsInput(BaseModel):
    """Input schema for financial metrics tool."""
    purchase_price: Optional[float] = Field(None, description="Purchase price (override Zestimate if provided)")
    down_payment_pct: float = Field(..., description="Down payment percentage (0-100)")
    loan_term_years: int = Field(..., description="Loan term in years")
    interest_rate: Optional[float] = Field(None, description="Annual interest rate % (default 6.85)")
    estimated_rent: Optional[float] = Field(None, description="Estimated monthly rent (override RentCast if provided)")
    time_horizon_years: int = Field(..., description="Investment time horizon years (unused in current metrics)")

    zestimate: Optional[float] = Field(None, description="Zillow Zestimate")
    rent_estimate: Optional[float] = Field(None, description="RentCast rent estimate")
    tax_annual: Optional[float] = Field(None, description="Annual property taxes from Zillow")
    hoa_monthly: Optional[float] = Field(None, description="Monthly HOA fee from Zillow")