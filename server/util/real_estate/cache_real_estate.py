from datetime import datetime

from langgraph.types import CachePolicy
from util.logger import get_logger

logger = get_logger(__name__)

# TTL configurations (in seconds)
# These are chosen based on how frequently real estate data meaningfully changes
TTL_SHORT     = 300      # 5 minutes   - very short-lived / volatile data 
TTL_MEDIUM    = 1800     # 30 minutes  - moderately time-sensitive 
TTL_LONG      = 3600     # 1 hour      - stable data
TTL_VERY_LONG = 7200     # 2 hours     - suitable for slowly-changing neighborhood/market data


def get_current_date_bucket() -> str:
    """
    Get a date bucket string for cache key inclusion.

    Causes cache invalidation at midnight (day boundaries).
    Useful for data that updates daily or less frequently (market stats, crime indexes, school ratings).

    Returns:
        Date string in YYYY-MM-DD format
    """
    return datetime.now().strftime("%Y-%m-%d")


def get_hour_bucket() -> str:
    """
    Get an hour bucket string for cache key inclusion.

    Causes cache invalidation at the top of each hour.
    Appropriate for data where intraday changes are possible but rare (e.g. active listings, price changes).

    Returns:
        Hour string in YYYY-MM-DD-HH format
    """
    return datetime.now().strftime("%Y-%m-%d-%H")


def create_cache_policy(ttl: int, static_key: str | None = None) -> CachePolicy:
    """
    General-purpose cache policy factory (fallback / utility).

    Args:
        ttl: Time to live in seconds
        static_key: If provided, uses this fixed key string (ignores state/address)

    Returns:
        CachePolicy instance suitable for most nodes when no special bucketing is needed
    """
    if static_key:
        return CachePolicy(key_func=lambda x: static_key.encode(), ttl=ttl)

    # Handle both dict (graph drawing) and object (execution) state representations
    def key_func(x):
        if isinstance(x, dict):
            # Graceful fallback when state is incomplete (e.g. during graph visualization)
            address = x.get("address", "default")
            return f"{address}".encode()
        return f"{x.address}".encode()

    return CachePolicy(key_func=key_func, ttl=ttl)


def create_property_cache_policy() -> CachePolicy:
    """
    Cache policy for core property data retrieval (Zillow, RentCast, etc.).

    Key includes hourly bucket because:
    - Active listing status, asking price, days on market can change intraday
    - Prevents serving stale "for sale" status after a property goes pending/off-market

    TTL: 1 hour — frequent enough to catch meaningful updates, infrequent enough to respect API rate limits
    """
    def key_func(x):
        if isinstance(x, dict):
            address = x.get("address", "default")
        else:
            address = x.address

        hour_bucket = get_hour_bucket()
        return f"{address}:{hour_bucket}".encode()

    return CachePolicy(key_func=key_func, ttl=TTL_LONG)


def create_financial_cache_policy() -> CachePolicy:
    """
    Cache policy for financial/investment analysis (cap rate, cash-on-cash return, IRR, etc.).

    IMPORTANT: Includes all user-supplied investment assumptions in the cache key.
    If any of purchase price, down payment %, rent estimate, interest rate, etc. changes,
    MUST recompute — otherwise user gets wrong/inconsistent numbers.

    Uses 1-hour TTL since core property data rarely changes within that window,
    but user assumptions can vary between requests.
    """
    def key_func(x):
        if isinstance(x, dict):
            address = x.get("address", "default")
            purchase_price      = x.get("purchase_price")      or 0
            down_payment_pct    = x.get("down_payment_pct")    or 20.0
            loan_term_years     = x.get("loan_term_years")     or 30
            interest_rate       = x.get("interest_rate")       or 0.0
            estimated_rent      = x.get("estimated_rent")      or 0
            time_horizon_years  = x.get("time_horizon_years")  or 10

            # Concatenate all variable inputs that affect the calculation
            param_str = (
                f"{purchase_price}:"
                f"{down_payment_pct}:"
                f"{loan_term_years}:"
                f"{interest_rate}:"
                f"{estimated_rent}:"
                f"{time_horizon_years}"
            )
            return f"financial:{address}:{param_str}".encode()

        else:
            # Pydantic model / object path
            address = x.address
            purchase_price      = getattr(x, "purchase_price",     0) or 0
            down_payment_pct    = getattr(x, "down_payment_pct",   20.0) or 20.0
            loan_term_years     = getattr(x, "loan_term_years",    30) or 30
            interest_rate       = getattr(x, "interest_rate",      0.0) or 0.0
            estimated_rent      = getattr(x, "estimated_rent",     0) or 0
            time_horizon_years  = getattr(x, "time_horizon_years", 10) or 10

            param_str = (
                f"{purchase_price}:"
                f"{down_payment_pct}:"
                f"{loan_term_years}:"
                f"{interest_rate}:"
                f"{estimated_rent}:"
                f"{time_horizon_years}"
            )
            return f"financial:{address}:{param_str}".encode()

    return CachePolicy(key_func=key_func, ttl=TTL_LONG)


def create_market_cache_policy() -> CachePolicy:
    """
    Cache policy for local market trends / comparables analysis.

    Uses daily bucket because:
    - Median prices, inventory levels, DOM, absorption rates typically update daily or weekly
    - Neighborhood-level comps don't change hour-to-hour

    Per-address key (not global) because different cities/zip codes have independent trends
    """
    def key_func(x):
        if isinstance(x, dict):
            address = x.get("address", "default")
        else:
            address = x.address

        date_bucket = get_current_date_bucket()
        return f"market:{address}:{date_bucket}".encode()

    return CachePolicy(key_func=key_func, ttl=TTL_VERY_LONG)


def create_risk_cache_policy() -> CachePolicy:
    """
    Cache policy for risk / livability factors (crime rates, school ratings, flood/fire risk, etc.).

    Uses daily bucket because:
    - Crime statistics, school ratings, Walk Score, etc. update very infrequently (weekly/monthly/quarterly)
    - Neighborhood risk profile is extremely stable over short timeframes

    2-hour TTL gives plenty of freshness while maximizing cache hit rate
    """
    def key_func(x):
        if isinstance(x, dict):
            address = x.get("address", "default")
        else:
            address = x.address

        date_bucket = get_current_date_bucket()
        return f"risk:{address}:{date_bucket}".encode()

    return CachePolicy(key_func=key_func, ttl=TTL_VERY_LONG)