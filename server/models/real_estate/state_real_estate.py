from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class Recommendation(str, Enum):
    BUY = "BUY"
    NEUTRAL = "NEUTRAL"
    PASS = "PASS"

class RealEstateResearchState(BaseModel):
    """State for real estate investment analysis workflow"""
    address: str
    purchase_price: Optional[float] = None         
    down_payment_pct: Optional[float] = 20.0
    loan_term_years: Optional[int] = 30
    interest_rate: Optional[float] = None           
    estimated_rent: Optional[float] = None         
    time_horizon_years: Optional[int] = 10

    # Agent outputs
    property_details: Optional[str] = None
    market_trends: Optional[str] = None
    financial_analysis: Optional[str] = None
    risk_assessment: Optional[str] = None
    comps_analysis: Optional[str] = None
    combined_analysis: Optional[str] = None

    # Evaluation loop
    compliant: bool = False
    feedback: Optional[str] = None
    revision_iteration_count: int = 0

    # Metadata
    is_address_valid: bool = False
    zpid: Optional[int] = None
    property_data: Optional[Dict[str, Any]] = None
    zillow_raw: Optional[Dict] = None
    rentcast_raw: Optional[Dict] = None       
    data_retrieved: bool = False

    # Extracted from data retrieval
    tax_annual: Optional[float] = None
    hoa_monthly: Optional[float] = None
    zestimate: Optional[float] = None
    rent_estimate: Optional[float] = None

    # ── Location (resolved from Zillow property response) ──────────────────────
    zip_code: Optional[str] = None          # e.g. "89135"
    city: Optional[str] = None
    state: Optional[str] = None             # e.g. "NV" – consider renaming to state_abbr if you want to avoid name collision risk

    # ── Zillow Housing Market / Trends Data ───────────────────────────────────
    zillow_market_raw: Optional[dict] = None          # Full raw JSON response from /housing_market endpoint

    # Key extracted scalars from market_overview (most useful for agents/prompts)
    market_typical_value: Optional[float] = None      # ZHVI / typical home value
    market_description: Optional[str] = None          # The human-readable summary paragraph
    market_yoy_change_pct: Optional[float] = None     # Parsed YoY % (positive or negative)
    market_inventory: Optional[int] = None            # For-sale inventory count
    market_days_pending: Optional[int] = None         # Median days to pending
    market_median_sale: Optional[float] = None        # Median sale price
    market_median_list: Optional[float] = None        # Median list price
    market_sale_to_list: Optional[float] = None       # Sale-to-list ratio

    crime_raw: Optional[Dict] = None
    crime_overall_grade: Optional[str] = None
    crime_violent_grade: Optional[str] = None
    crime_property_grade: Optional[str] = None

    schools_raw: Optional[List[Dict]] = None
    elementary_school_name: Optional[str] = None
    elementary_school_rating: Optional[int] = None
    middle_school_name: Optional[str] = None
    middle_school_rating: Optional[int] = None
    high_school_name: Optional[str] = None
    high_school_rating: Optional[int] = None