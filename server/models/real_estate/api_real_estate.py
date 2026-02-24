from pydantic import BaseModel
from typing import Optional

class RealEstateResearchRequest(BaseModel):
    address: str
    purchase_price: Optional[float] = None
    down_payment_pct: float = 20.0
    loan_term_years: int = 30
    interest_rate: Optional[float] = None
    estimated_rent: Optional[float] = None
    time_horizon_years: int = 10