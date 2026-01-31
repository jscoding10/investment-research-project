import yfinance as yf

from util.logger import get_logger
from models.crypto.state_crypto import CryptoResearchState

logger = get_logger(__name__)

def validate_ticker(ticker: str, state: CryptoResearchState) -> dict:
    try:
        yf_ticker = yf.Ticker(state.ticker)
        info = yf_ticker.info
        
        is_valid = bool("longName" in info and info["longName"] is not None)

        if is_valid:
            # Try to remove " USD" suffix from ticker
            raw_name = info.get("longName") or info.get("shortName") or state.ticker
            clean_name = raw_name.replace(" USD", "").replace(" usd", "").strip()
            
            return {
                "is_ticker_valid": True,
                "name": clean_name,                    
                "ticker_info": info,
            }
        
        else:
            return {"is_ticker_valid": False}
            
    except Exception as e:
        logger.warning(f"Ticker validation failed for {ticker}: {e}")
        return {"is_ticker_valid": False}