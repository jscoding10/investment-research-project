import os
import re
from dotenv import load_dotenv
import requests
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
from models.crypto.api_crypto import CryptoResearchRequest
from graph_crypto import research_chain_crypto
from models.real_estate.api_real_estate import RealEstateResearchRequest  
from graph_real_estate import research_chain_real_estate
import yfinance as yf
from datetime import datetime

import re
from fastapi import HTTPException

from util.logger import get_logger

logger = get_logger(__name__)

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



ADDRESS_PATTERN = re.compile(r'^[\w\s,.-/#&()\'"]{5,200}$', re.IGNORECASE)
# Allows: letters, numbers, spaces, commas, periods, hyphens, slashes, #, &, parentheses, quotes
# Length: min 5 chars (e.g. "123 Main"), max 200 (very long addresses)

def sanitize_address(address: str) -> str:
    """
    Sanitize and lightly validate real estate address input.
    Normalizes whitespace, removes leading/trailing junk, - keeps most formatting.
    """
    if not isinstance(address, str):
        raise HTTPException(status_code=400, detail="Address must be a string")

    # Strip leading and trailing whitespace
    sanitized = address.strip()

    if not sanitized:
        raise HTTPException(status_code=400, detail="Address cannot be empty")

    # Normalize multiple spaces / tabs / newlines → single space
    sanitized = re.sub(r'\s+', ' ', sanitized)

    # Remove trailing punctuation that is very unlikely in real addresses
    sanitized = sanitized.rstrip(',.;')

    # Basic format check
    if not ADDRESS_PATTERN.match(sanitized):
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid address format. Address should contain only letters, numbers, "
                "spaces, and common punctuation (.,-/#&'\"). Minimum 5 characters."
            )
        )

    # Consistent casing 
    # sanitized = sanitized.title()   # uncomment if you want "123 Main St" instead of "123 main st"

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

# Stock equity research endpoint 
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


# Crypto equity research endpoint 
@api.post("/research-crypto") 
@limiter.limit("10/minute")
async def research_crypto(request: Request, req: CryptoResearchRequest):  

    sanitized_ticker = sanitize_ticker(req.ticker)

    res = await research_chain_crypto.ainvoke(
        {
            "ticker": sanitized_ticker,
            "trade_duration": req.trade_duration,
            "trade_direction": req.trade_direction,
        }
    )
    return {
        "ticker": res.ticker,
        "sentiment_analysis": {  
            "technical": res.technical_sentiment, 
            "macro": res.macro_sentiment,
            "peer": res.peer_sentiment,
            "news": res.news_sentiment,
        },
        "combined_sentiment": res.combined_sentiment,
    }

@api.post("/research-real-estate")
@limiter.limit("10/minute")
async def research_real_estate(request: Request, req: RealEstateResearchRequest):
    try:
        sanitized_address = sanitize_address(req.address)
        
        res = await research_chain_real_estate.ainvoke(
            {
                "address": sanitized_address,
                "purchase_price": req.purchase_price,
                "down_payment_pct": req.down_payment_pct,
                "loan_term_years": req.loan_term_years,
                "interest_rate": req.interest_rate,
                "estimated_rent": req.estimated_rent,
                "time_horizon_years": req.time_horizon_years,
            }
        )
        return {
            "address": res.address,
            "analysis": {
                "market": res.market_trends,
                "financial": res.financial_analysis,
                "risk": res.risk_assessment,
            },
            "combined_analysis": res.combined_analysis,
        } 
    except HTTPException as he:
        raise he  
    except Exception as e:
        logger.error(f"Real estate research failed: {e}", exc_info=True)
        raise HTTPException(500, detail="Internal error during analysis. Please try again later.")
    
# Ticker search endpoint for autocomplete 
@api.get("/ticker-search")
async def ticker_search(q: str = ""):
    query = q.strip().upper() if q else ""
    
    if not query: 
        return []

    results = []
    seen = set()

    try:
        # Exact match search for short ticker names
        ticker = yf.Ticker(query)
        info = ticker.info
        name = info.get("longName") or info.get("shortName") or query
        
        if name and name.lower() != query.lower():  # Valid company name found
            results.append({"symbol": query, "name": name})
            seen.add(query)

        # Partial prefix search when 3 to 5 characters
        if 3 <= len(query) <= 5:
            search_data = yf.utils.get_json(
                f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&quotesCount=10&newsCount=0"
            )

            for item in search_data.get("quotes", [])[:10]:
                if item.get("typeDisp") not in ["Equity", "ETF"]:
                    continue
                    
                symbol = item.get("symbol", "").split(".")[0].upper()
                if symbol in seen or not symbol.startswith(query):
                    continue
                    
                seen.add(symbol)

                # Try to extract name from search result
                name = item.get("longname") or item.get("shortname") or symbol
                if name == symbol:
                    try:
                        fallback_info = yf.Ticker(symbol).info
                        name = fallback_info.get("longName") or fallback_info.get("shortName") or symbol
                    except:
                        pass 
                        
                results.append({"symbol": symbol, "name": name})

    except Exception as e:
        # Use proper logging in production
        print(f"Ticker search error for '{query}': {e}")

    return results[:6]

@api.get("/crypto-ticker-search")
async def crypto_ticker_search(q: str = ""):
    query = q.strip().upper() if q else ""
    
    if not query:
        return []

    results = []
    seen = set()

    try:
        # 1. Quick exact / prefix-style match: always try {query}-USD pattern first
        # This catches BTC → BTC-USD, ETH → ETH-USD, etc. reliably
        crypto_symbol = f"{query}-USD"
        if crypto_symbol not in seen:
            try:
                ticker = yf.Ticker(crypto_symbol)
                info = ticker.info or {}
                
                # Simple check: if we get valid info and it's crypto-like
                if info.get("regularMarketPrice") or info.get("quoteType") == "CRYPTOCURRENCY":
                    name = info.get("longName") or info.get("shortName") or f"{query} USD"
                    results.append({"symbol": crypto_symbol, "name": name})
                    seen.add(crypto_symbol)
            except:
                pass

        # 2. If short query or exact didn't work → try the search API (like stock version)
        if len(query) >= 2 and len(results) == 0:  # or always do it if you want more results
            search_data = yf.utils.get_json(
                f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&quotesCount=10&newsCount=0"
            )

            for item in search_data.get("quotes", [])[:10]:
                symbol = item.get("symbol", "").upper()
                if symbol in seen:
                    continue

                # Accept only clear crypto items
                if (
                    item.get("quoteType") == "CRYPTOCURRENCY"
                    or item.get("typeDisp") in ["Cryptocurrency", "Crypto"]
                    or "-USD" in symbol
                ):
                    seen.add(symbol)

                    name = (
                        item.get("longname")
                        or item.get("shortname")
                        or item.get("name")
                        or symbol
                    )

                    # Quick fallback for bad names
                    if name == symbol or "USD" in name.upper():
                        try:
                            fallback_info = yf.Ticker(symbol).info
                            name = fallback_info.get("longName") or fallback_info.get("shortName") or name
                        except:
                            pass

                    results.append({"symbol": symbol, "name": name})

        # Limit and return (no reordering for simplicity)
        return results[:6]

    except Exception as e:
        print(f"Crypto ticker search error for '{query}': {e}")
        return []
    
@api.get("/address-search")
def address_search(q: str = ""):  
    query = q.strip()
    
    if not query:
        return []

    url = "https://us-autocomplete-pro.api.smarty.com/lookup"
    params = {
        "auth-id": os.getenv("SMARTY_AUTH_ID"),
        "auth-token": os.getenv("SMARTY_AUTH_TOKEN"),
        "search": query,
        "max_results": 10,
    }

    try:
        resp = requests.get(url, params=params, timeout=10)  
        resp.raise_for_status()  
        data = resp.json()

        suggestions = data.get("suggestions", [])
        formatted = []

        for sug in suggestions:
            secondary = sug.get("secondary", "")
            entries = sug.get("entries", 0)
            if entries > 1:
                display = f"{sug['street_line']} (Multiple units), {sug['city']}, {sug['state']} {sug['zipcode']}"
            else:
                display = f"{sug['street_line']} {secondary}, {sug['city']}, {sug['state']} {sug['zipcode']}".strip()

            formatted.append({
                "display": display,
                "street": sug['street_line'],
                "secondary": secondary,
                "city": sug['city'],
                "state": sug['state'],
                "zipcode": sug['zipcode'],
                "entries": entries
            })

        return formatted

    except requests.exceptions.RequestException as e:
        logger.error(f"Smarty address search failed: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error in address search: {e}")
        return []
    
# Stock table endpoint
MAG7 = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]

@api.get("/stock-table-prices")
async def get_portfolio_prices():
    """
    Blazing fast: ~500ms instead of 5s
    Uses parallel downloads + bulk data fetch
    """
    # Step 1: Download ALL price data in ONE request (this is the killer optimization)
    data = yf.download(
        tickers=" ".join(MAG7),
        period="2d",
        interval="1m",        # gives latest price even in pre-market
        group_by="ticker",
        auto_adjust=True,
        threads=True,         # parallel HTTP requests (default in newer yfinance)
        progress=False
    )

    results = []
    failed = []

    for symbol in MAG7:
        try:
            ticker_data = data[symbol] if len(MAG7) > 1 else data

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

# Crypto table endpoint
# Tickers are in Yahoo Finance format: SYMBOL-USD
TOP_CRYPTO = [
    "BTC-USD",   # Bitcoin
    "ETH-USD",   # Ethereum
    "BNB-USD",   # BNB
    "SOL-USD",   # Solana
    "XRP-USD",   # XRP
    "ADA-USD",   # Cardano
    "TRX-USD"    # TRON (often in top 10)
]

@api.get("/crypto-table-prices")
async def get_crypto_prices():
    """
    Fast crypto price table using yfinance bulk download
    Optimized: single bulk request for all prices + parallel threads
    """
    import yfinance as yf
    from datetime import datetime

    # Step 1: Bulk download recent data (2 days to ensure previous close even on weekends/holidays)
    data = yf.download(
        tickers=" ".join(TOP_CRYPTO),
        period="2d",
        interval="5m",        # Higher resolution for more recent data points (crypto is 24/7)
        group_by="ticker",
        auto_adjust=True,
        threads=True,         # Parallel downloads – big speed boost
        progress=False
    )

    results = []
    failed = []

    for symbol in TOP_CRYPTO:
        try:
            ticker_data = data[symbol] if len(TOP_CRYPTO) > 1 else data

            if ticker_data.empty or "Close" not in ticker_data.columns:
                failed.append(symbol)
                continue

            close = ticker_data["Close"]
            latest = close.iloc[-1]
            previous = close.iloc[-2] if len(close) > 1 else latest  # Fallback if only one data point

            # 24h change % (crypto typically uses previous day close - here use latest vs previous point)
            change_pct = round((latest / previous - 1) * 100, 2) if previous != 0 else 0

            # Fast info (much quicker than full .info)
            t = yf.Ticker(symbol)
            info = t.info

            results.append({
                "ticker": symbol.replace("-USD", ""),
                "name": info.get("longName") or info.get("shortName", symbol),
                "price": round(float(latest), 6 if "USDT" in symbol or "USDC" in symbol else 2),  # More decimals for non-stablecoins
                "change_pct": change_pct,
                "volume": int(ticker_data["Volume"].iloc[-1]) if "Volume" in ticker_data.columns else 0,
                "currency": info.get("currency", "USD")
            })
        except Exception:
            failed.append(symbol)

    return {
        "data": results,
        "failed": failed,
        "updated": datetime.utcnow().isoformat() + "Z",
        "source": "yfinance (Yahoo Finance crypto data - bulk download + fast_info)"
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