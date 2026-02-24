from datetime import datetime
from typing import Any, Dict, Optional
from langgraph.types import CachePolicy
from util.logger import get_logger

logger = get_logger(__name__)

# TTL configurations (in seconds)
TTL_SHORT = 300  # 5 min
TTL_MEDIUM = 1800  # 30 min
TTL_LONG = 3600  # 1 hour
TTL_VERY_LONG = 7200  # 2 hours

def get_current_date_bucket() -> str:
    return datetime.now().strftime("%Y-%m-%d")

def get_hour_bucket() -> str:
    return datetime.now().strftime("%Y-%m-%d-%H")

def create_cache_policy(ttl: int, static_key: str | None = None) -> CachePolicy:
    if static_key:
        return CachePolicy(key_func=lambda x: static_key.encode(), ttl=ttl)
    def key_func(x):
        if isinstance(x, dict):
            address = x.get("address", "default")
            return f"{address}".encode()
        return f"{x.address}".encode()
    return CachePolicy(key_func=key_func, ttl=ttl)

def create_property_cache_policy() -> CachePolicy:
    def key_func(x):
        if isinstance(x, dict):
            address = x.get("address", "default")
        else:
            address = x.address
        hour_bucket = get_hour_bucket()
        return f"{address}:{hour_bucket}".encode()
    return CachePolicy(key_func=key_func, ttl=TTL_MEDIUM)

def create_market_cache_policy() -> CachePolicy:
    def key_func(x):
        date_bucket = get_current_date_bucket()
        return f"market:{date_bucket}".encode()
    return CachePolicy(key_func=key_func, ttl=TTL_VERY_LONG)