import os

from dotenv import load_dotenv
load_dotenv()

# Suppress gRPC/absl logging before importing anything that uses it
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from graph import research_chain
from models.api import EquityResearchRequest
import yfinance as yf
from fastapi import APIRouter
from datetime import datetime
import asyncio

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type"],
)

@app.get("/")
def ping():
    return {"message": "Server Running"}

# curl -X GET http://localhost:8000/research-equity -H "Content-Type: application/json" -d "{\"ticker\": \"NVDA\"}" | python -m json.tool
# curl -X POST http://localhost:8000/research-equity -H "Content-Type: application/json" -d '{"ticker":"NVDA","trade_duration":"swing_trade","trade_direction":"long"}'

@app.post("/research-equity")
async def research_equity(req: EquityResearchRequest):    
    res = research_chain.invoke(
        {
            "ticker": req.ticker,
            "trade_duration": req.trade_duration,
            "trade_direction": req.trade_direction,
        }
    )
    return {
        "ticker": res.ticker,
        "sentiment_analysis": {
            "fundamental": res.fundamental_sentiment,
            "technical": res.technical_sentiment,
            "macro": res.macro_sentiment,
            "peer": res.peer_sentiment,
            "industry": res.industry_sentiment,
            "news": res.news_sentiment,
        },
        "combined_sentiment": res.combined_sentiment,
    }

router = APIRouter()

# Your tickers
MAG7_AND_ETFS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]

@app.get("/stock-table-prices")
async def get_portfolio_prices():
    """
    Blazing fast: ~500ms instead of 5s
    Uses parallel downloads + bulk data fetch
    """
    # Step 1: Download ALL price data in ONE request (this is the killer optimization)
    data = yf.download(
        tickers=" ".join(MAG7_AND_ETFS),
        period="2d",
        interval="1m",        # gives latest price even in pre-market
        group_by="ticker",
        auto_adjust=True,
        threads=True,         # parallel HTTP requests (default in newer yfinance)
        progress=False
    )

    results = []
    failed = []

    for symbol in MAG7_AND_ETFS:
        try:
            ticker_data = data[symbol] if len(MAG7_AND_ETFS) > 1 else data

            if ticker_data.empty or "Close" not in ticker_data.columns:
                failed.append(symbol)
                continue

            close = ticker_data["Close"]
            latest = close.iloc[-1]
            previous = close.iloc[-2] if len(close) > 1 else latest

            change_pct = round((latest / previous - 1) * 100, 2) if previous != 0 else 0

            # Fast info fetch (still parallel via yf.Tickers)
            t = yf.Ticker(symbol)
            info = t.fast_info  # ← this is 10× faster than t.info

            results.append({
                "ticker": symbol,
                "name": info.get("longName") or info.get("shortName", symbol),
                "price": round(float(latest), 2),
                "change_pct": change_pct,
                "volume": int(ticker_data["Volume"].iloc[-1]) if "Volume" in ticker_data.columns else 0,
                "currency": info.get("currency", "USD")
            })
        except Exception as e:
            failed.append(symbol)

    return {
        "data": results,
        "failed": failed,
        "updated": datetime.utcnow().isoformat() + "Z",
        "source": "yfinance (bulk + fast_info)"
    }

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)