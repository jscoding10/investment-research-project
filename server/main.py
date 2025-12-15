import os
import re
from dotenv import load_dotenv
load_dotenv()

# Suppress gRPC/absl logging before importing anything that uses it
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"
# os.environ["TOKENIZERS_PARALLELISM"] = "false"

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.exceptions import HTTPException
from pathlib import Path
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from graph import research_chain
from models.api import EquityResearchRequest
import yfinance as yf
from datetime import datetime

TICKER_PATTERN = re.compile(r"^[A-Z0-9.\-]{1,10}$")


def sanitize_ticker(ticker: str) -> str:
    """Sanitize and validate stock ticker input."""
    sanitized = ticker.strip().upper()

    if not sanitized:
        raise HTTPException(status_code=400, detail="Ticker cannot be empty")

    if not TICKER_PATTERN.match(sanitized):
        raise HTTPException(
            status_code=400,
            detail="Invalid ticker format. Ticker must contain only letters, numbers, dots, or hyphens (max 10 characters)",
        )

    return sanitized


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type"],
)

# api routes all prefixed with api
###################################### Render #######################################
api = FastAPI()
######################################################################################
@api.get("/")
def ping():
    return {"message": "Server Running"}

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# curl -X GET http://localhost:8000/research-equity -H "Content-Type: application/json" -d "{\"ticker\": \"NVDA\"}" | python -m json.tool
# curl -X POST http://localhost:8000/research-equity -H "Content-Type: application/json" -d '{"ticker":"NVDA","trade_duration":"swing_trade","trade_direction":"long"}'

# Stock equity research endpoint - used to be app
@api.post("/research-equity")
@limiter.limit("10/minute")
async def research_equity(request: Request, req: EquityResearchRequest):  

    sanitized_ticker = sanitize_ticker(req.ticker)

    res = await research_chain.ainvoke(
        {
            "ticker": sanitized_ticker,
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
            # "filings": res.filings_sentiment,
        },
        "combined_sentiment": res.combined_sentiment,
    }

# Stock table endpoint
MAG7_AND_ETFS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]

@api.get("/stock-table-prices")
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

@api.get("/debug/industry")
async def debug_industry(ticker: str = "NVDA", industry: str = "Semiconductors"):
    from agents.industry.agent import get_industry_sentiment
    result = get_industry_sentiment(ticker=ticker, industry=industry)
    return {"ticker": ticker,  "result": result}  

@api.get("/debug/peer")
async def debug_peer(ticker: str = "AAPL", business: str= "Apple Inc."):
    """
    Quick test endpoint to run ONLY the peer agent in isolation.
    Example: http://localhost:8000/debug/peer?ticker=AAPL&business=Apple Inc.
    """
    from agents.peer.agent import get_peer_sentiment
    
    result = get_peer_sentiment(ticker=ticker, business=business)
    
    return {
        "ticker": ticker,
  
        "result": result
    } 

@api.get("/debug/news")
async def debug_news(ticker: str = "LLY", business: str= "Eli Lilly and Company"):
    """
    Quick test endpoint to run ONLY the news agent in isolation.
    Example: http://localhost:8000/debug/news?ticker=AAPL&business=Apple Inc.
    """
    from agents.news.agent import get_news_sentiment
    
    result = get_news_sentiment(ticker=ticker, business=business)
    
    return {
        "ticker": ticker,
  
        "result": result
    }
######################################################### Render ###################################################################
# Mount the /api router
app.mount("/api", api)

static_dir = Path(__file__).parent / "static"

if static_dir.exists() and list(static_dir.iterdir()):
    print(f"Production mode - serving Angular from {static_dir}")

    # Serve all static files directly (no html=True)
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # Serve root files (JS/CSS) and fallback to index.html for SPA routes
    @app.get("/{full_path:path}")
    async def serve_angular(full_path: str):
        file_path = static_dir / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        # Fallback to index.html for any unknown path (SPA routing)
        index_path = static_dir / "index.html"
        if index_path.is_file():
            return FileResponse(index_path)
        raise HTTPException(status_code=404, detail="Not Found")
else:
    print("Development mode - static/ not found. Use 'ng serve' for frontend.")
    @app.get("/")
    async def dev_message():
        return {
            "message": "Backend running. Start Angular with 'npm start' in /client folder",
            "api_docs": "/docs",
            "frontend_hint": "http://localhost:4200"
        }
##########################################################################################################################################
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)