from pydantic import BaseModel

from models.crypto.state_crypto import TradeDirection, TradeDuration


class CryptoResearchRequest(BaseModel):
    """Request model for crypto research endpoint."""

    ticker: str
    trade_duration: TradeDuration
    trade_direction: TradeDirection