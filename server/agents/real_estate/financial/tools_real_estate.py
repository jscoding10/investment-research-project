from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, Optional

from langchain_core.tools import Tool
from models.real_estate.tools_real_estate import FinancialMetricsInput 

from util.logger import get_logger

logger = get_logger(__name__)

def compute_financial_metrics(
    purchase_price: Optional[float],
    down_payment_pct: float,
    loan_term_years: int,
    interest_rate: Optional[float],
    estimated_rent: Optional[float],
    time_horizon_years: int,
    zestimate: Optional[float] = None,
    rent_estimate: Optional[float] = None,
    tax_annual: Optional[float] = None,
    hoa_monthly: Optional[float] = None,
) -> dict:
    """
    Pure deterministic calculations using provided inputs + raw data dicts.
    No LLM involvement here — only math.
    """
    try:
        # Price hierarchy: user override → zestimate → fail
        price = Decimal(str(purchase_price or zestimate or 0))
        if price <= 0:
            raise ValueError("No valid purchase price (neither user input nor Zestimate)")

        # Rent hierarchy: user override → rent_estimate → fail
        rent_mo = Decimal(str(estimated_rent or rent_estimate or 0))
        if rent_mo <= 0:
            raise ValueError("No valid rent estimate")

        # Expenses (now directly from state)
        taxes_yr = Decimal(str(tax_annual or 0))
        hoa_mo = Decimal(str(hoa_monthly or 0))

        # Defaults / fallbacks
        down_pct = Decimal(str(down_payment_pct)) / 100
        loan_term_yr = loan_term_years
        interest_rate = Decimal(str(interest_rate or 6.85)) / 100  # annual %
        vacancy_pct = Decimal("0.08")  # 8% default
        maint_pct = Decimal("0.015")   # 1.5% of value
        insurance_yr = Decimal("1200")  # rough annual avg; improve later

        # Mortgage calculation
        loan_amt = price * (1 - down_pct)
        rate_mo = interest_rate / 12
        n = loan_term_yr * 12
        if rate_mo == 0:
            mortgage_mo = loan_amt / n
        else:
            mortgage_mo = loan_amt * (rate_mo * (1 + rate_mo)**n) / ((1 + rate_mo)**n - 1)

        # Monthly expenses
        taxes_mo = taxes_yr / 12
        insurance_mo = insurance_yr / 12
        maint_mo = price * maint_pct / 12
        vacancy_mo = rent_mo * vacancy_pct
        total_exp_mo = mortgage_mo + taxes_mo + hoa_mo + insurance_mo + maint_mo + vacancy_mo

        # Key metrics
        noi_yr = (rent_mo * 12) - (total_exp_mo * 12)
        cap_rate = (noi_yr / price) * 100 if price else Decimal("0")
        cash_flow_yr = noi_yr  # Already net of expenses including vacancy
        invested = price * down_pct
        cash_on_cash = (cash_flow_yr / invested) * 100 if invested else Decimal("0")
        breakeven_occ = (total_exp_mo / rent_mo) * 100 if rent_mo else Decimal("0")

        # Simple appreciation proxy for total return (optional)
        assumed_apprec_yr = price * Decimal("0.03")  # 3% default
        total_return_yr = cash_flow_yr + assumed_apprec_yr
        irr_proxy = (total_return_yr / invested) * 100 if invested else Decimal("0")

        # return {
        #     "purchase_price": float(price),
        #     "rent_monthly": float(rent_mo),
        #     "mortgage_monthly": float(mortgage_mo.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
        #     "total_expenses_monthly": float(total_exp_mo.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
        #     "noi_annual": float(noi_yr.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
        #     "cap_rate_pct": float(cap_rate.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)),
        #     "cash_on_cash_pct": float(cash_on_cash.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)),
        #     "breakeven_occupancy_pct": float(breakeven_occ.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)),
        #     "irr_proxy_pct": float(irr_proxy.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)),
        #     "recommendation": (
        #         "Strong" if cap_rate > 7 and cash_on_cash > 8 else
        #         "Marginal" if cap_rate > 5 and cash_on_cash > 5 else
        #         "Negative"
        #     )
        # }

        return {
            "purchase_price": float(price),
            "rent_monthly": float(rent_mo),
            "mortgage_monthly": float(mortgage_mo.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            "total_expenses_monthly": float(total_exp_mo.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            "noi_annual": float(noi_yr.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            "cap_rate_pct": float(cap_rate.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)),
            "cash_on_cash_pct": float(cash_on_cash.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)),
            "breakeven_occupancy_pct": float(breakeven_occ.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)),
            "irr_proxy_pct": float(irr_proxy.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)),
            "recommendation": (
                # High-equity deals (>40% down) get easier thresholds
                "Strong" if (down_pct >= Decimal("0.4") and cash_on_cash >= Decimal("5.5")) or 
                           (down_pct < Decimal("0.4") and cap_rate > Decimal("7") and cash_on_cash > Decimal("8"))
                else
                "Marginal" if (down_pct >= Decimal("0.4") and cash_on_cash >= Decimal("4")) or 
                             (down_pct < Decimal("0.4") and cap_rate > Decimal("5") and cash_on_cash > Decimal("5"))
                else
                "Negative"
            )
        }

    except Exception as e:
        return {"error": str(e)}

get_financial_metrics_tool = Tool(
    name="get_financial_metrics_tool",
    description="Use this tool to compute real estate financial metrics (mortgage, NOI, cap rate, cash on cash, etc.) from user inputs and raw Zillow/RentCast data. Provide all required inputs including raw dicts.",
    func=compute_financial_metrics,
    args_schema=FinancialMetricsInput,  
)