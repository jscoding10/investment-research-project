# Conviction Insight

**Deployed version:** https://investment-research-project.onrender.com

Conviction Insight is a full-stack web application that implements an agentic AI structure to compile investment research reports across different asset classes.

⚠️ **Important Disclaimer**

This is an experimental AI research tool — **not financial advice**. LLM-based analysis can contain factual errors, hallucinations, outdated data, or biased reasoning.
Always do your own research and consult licensed professionals before making investment decisions.
Past performance is not indicative of future results.
The author assumes no liability for any losses.

**Currently supported asset classes:**

- **Stocks**: The user enters a stock ticker (e.g., NVDA), trade direction (long or short), and trade duration (day trade, swing trade, or position trade). The app produces a comprehensive report with sentiment analysis across fundamentals, technicals, macro factors, industry trends, peer comparison, and news sentiment, synthesizing an overall bullish, bearish, or neutral conviction.

- **Cryptocurrencies**: The user enters a crypto ticker (e.g., BTC-USD, ETH-USD), trade direction (long or short), and trade duration (day trade, swing trade, or position trade). The app produces a comprehensive report with sentiment analysis across technicals, macro factors, peer comparison, and news sentiment (fundamentals and industry not applicable), weighted by trade duration, synthesizing an overall bullish, bearish, or neutral conviction.

- **Real Estate**: The user enters a property address (e.g., 123 Main St, Las Vegas, NV 89101), optional purchase price, down payment percentage, estimated rent, and other financing assumptions. The app retrieves live property data, computes key rental investment metrics (cap rate, cash-on-cash return, breakeven occupancy), analyzes local market trends and neighborhood risk/livability, and synthesizes a clear strong buy, hold, or avoid recommendation for long-term buy-and-hold strategy.

The app features a clean, responsive UI, markdown-rendered reports, loading states, robust error handling, and one-click PDF export.

## Instructions

### Running Locally

1. Navigate to the project root.
2. Create a `.env` file **in the `server` folder** with required variables (e.g., Groq API key – see `server/.env.example`).
3. Set up a Python virtual environment **in the `server` folder** (Python 3.12 recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install backend dependencies **(from the server folder)**:

   ```
   pip install -r requirements.txt
   ```

5. Run the backend server:

   ```
   uvicorn main:app --reload --port 8000
   ```

   The API will run on http://localhost:8000.

6. In a separate terminal, navigate to the client folder (Angular app):

   ```
   cd client
   npm install
   ng serve
   ```

   The frontend will run on http://localhost:4200.

7. Open your browser to http://localhost:4200, enter a ticker like NVDA, select direction and duration, and generate a report.
   **API test examples:**

   Stocks:

   ```
   curl -X POST "http://localhost:8000/api/research-equity" -H "Content-Type: application/json" -d '{"ticker": "NVDA", "trade_duration": "swing_trade", "trade_direction": "long"}'
   ```

   Crypto:

   ```
   curl -X POST "http://localhost:8000/api/research-crypto" -H "Content-Type: application/json" -d '{"ticker": "BTC-USD", "trade_duration": "day_trade", "trade_direction": "short"}'
   ```

   Real Estate:

   ```
   curl -X POST "http://localhost:8000/api/research-real-estate" -H "Content-Type: application/json" -d '{"address": "123 Main St, Las Vegas, NV 89101", "purchase_price": 425000, "down_payment_pct": 25, "estimated_rent": 2200}'
   ```

### Running in Docker

This project uses a multi-stage Dockerfile to build the Angular frontend and serve it with the FastAPI backend in a single container.

To run the application locally with Docker, follow these steps:

1. Create a .env file in the project root with your required environment variables (e.g., Groq API Keys – see server/.env.example for details).
2. Ensure your local Docker daemon is running.
3. Build and run the container from the project root:

   ```
   docker build -t investment-research-project . docker run -p 8000:8000 --env-file .env investment-research-project
   ```

4. The application will be available at http://localhost:8000.

   To test the API directly, see the curl examples in the Running Locally section.

## Architecture

Conviction Insight uses a multi-agent LangGraph workflow to generate structured research reports. The graph validates the input, runs specialized agents in parallel, aggregates results, and iteratively refines the final output via an evaluator (up to 3 revisions for quality).

### Key Design Patterns

- **Tool-Use Agents:** Fetch structured data (yfinance, property APIs, FRED, etc.)
- **Web RAG / Search Agents:** Real-time external research via Groq Compound
- **Stateful Graph:** Parallel branches → aggregation → evaluator loop
- **Intelligent Caching:** Per-node TTLs (short for news/technicals, longer for fundamentals/property data)

### Client (Frontend)

<p>
    <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/angular/angular-original.svg" alt="Angular" width="30" align="left"/>
    <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/typescript/typescript-original.svg" alt="TypeScript" width="30" align="left"/>
    <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/tailwindcss/tailwindcss-original.svg" alt="Tailwind CSS" width="30" align="left"/>
</p>
<br>
<br>

- TypeScript + Angular Signals for reactive state
- Tailwind CSS for styling
- PrimeNG components for forms and UI
- Ngx-Markdown for report rendering
- Custom pdfmake pipeline for clean PDF exports

### Server (Backend)

<p>
    <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/fastapi/fastapi-original.svg" alt="FastAPI" width="30" align="left"/>
    <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/python/python-original.svg" alt="Python" width="30" align="left"/>
</p>
<br>
<br>

- FastAPI: Rate-limited endpoints, CORS, static serving of built Angular app
- LangGraph: Orchestrates agent workflow with conditional routing and revision loop
- yfinance: Real-time data and ticker validation
- Groq LLMs: Fast inference for all agents
- In-memory caching: Dynamic policies per node to reduce cost/latency

### Asset-Class Specific Agents

After parallel agent execution, a **Sentiment Aggregator** combines the results into a final recommendation (bullish/neutral/bearish for stocks & crypto; strong buy/hold/avoid for real estate), and a **Sentiment Evaluator** checks quality and triggers up to 3 revisions if necessary.

#### Stock Equity Research Agents

| Agent                | Focus                                          | Method                     |
| -------------------- | ---------------------------------------------- | -------------------------- |
| Fundamentals         | Financial statements, valuations               | yfinance tool calls        |
| Technical            | Price patterns, indicators (RSI, MACD)         | yfinance + computation     |
| Macro                | Economic indicators, rates                     | Structured data            |
| Industry             | Sector trends, headwinds                       | Web research               |
| Peer                 | Competitor comparison                          | Web research               |
| News                 | Recent headline and social sentiment           | Web research               |
| Sentiment Aggregator | Weighted synthesis: bullish/neutral/bearish    | LLM (iterative refinement) |
| Sentiment Evaluator  | Quality gate (format, decisiveness, grounding) | Structured LLM critique    |

#### Crypto Research Agents

| Agent                | Focus                                                  | Method                     |
| -------------------- | ------------------------------------------------------ | -------------------------- |
| Technical            | Price patterns, indicators (RSI, MACD, SMA, Bollinger) | yfinance + computation     |
| Macro                | Economic indicators, market conditions                 | Structured data            |
| Peer                 | Competitor comparison                                  | Web research               |
| News                 | Recent headline and market sentiment                   | Web research               |
| Sentiment Aggregator | Weighted synthesis: bullish/neutral/bearish            | LLM (iterative refinement) |
| Sentiment Evaluator  | Quality gate (format, decisiveness, grounding)         | Structured LLM critique    |

#### Real Estate Research Agents

| Agent                | Focus                                             | Method                             |
| -------------------- | ------------------------------------------------- | ---------------------------------- |
| Data Retrieval       | Property details, value, rent est, schools, crime | Zillow + RentCast + Crime APIs     |
| Financial Analysis   | Cap rate, cash-on-cash, NOI, breakeven, mortgage  | Custom deterministic tool + LLM    |
| Market Trends        | Local trends, inventory, YoY change, sentiment    | Zillow data + Groq Compound search |
| Risk Assessment      | Crime grades, schools, livability, recent signals | Extracted data + Groq Compound     |
| Sentiment Aggregator | Weighted synthesis: strong buy/hold/avoid         | LLM (iterative refinement)         |
| Sentiment Evaluator  | Quality gate (format, decisiveness, grounding)    | Structured LLM critique            |

## Optimizations

- Node-level caching (short TTL for volatile data like news/technicals, longer for property fundamentals)
- Bulk data fetching where possible (yfinance, property scalars)
- Efficient state management with Angular Signals to avoid unnecessary re-renders.
- Custom markdown normalization and pdfmake parsing for clean PDF exports.

## Lessons Learned

Developing Conviction Insight deepened my understanding of maintainable multi-agent workflows with LangGraph, particularly the importance of clean state handling, conditional edges, revision cycles, and cost-effective caching. The frontend stack (Angular Signals, PrimeNG, Tailwind) proved exceptionally productive for building responsive and refined UIs. Integrating real-time financial and property APIs also sharpened my skills in robust error handling, partial-result rendering, and graceful degradation.

## Future Plans

- User authentication and report history/saving
- Observability (LangSmith tracing)
- Expand to multifamily / commercial real estate
- Add unit/integration tests coverage
