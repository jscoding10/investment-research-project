# Conviction Insight

**Deployed version:** https://investment-research-project.onrender.com

Conviction Insight is a full-stack web application that implements an agentic AI structure to compile investment research reports across different asset classes.

Currently live for stocks: The user enters a stock ticker (e.g., NVDA), trade direction (long or short), and trade duration (day trade, swing trade, or position trade). The app produces a comprehensive report with sentiment analysis across fundamentals, technicals, macro factors, industry trends, peer comparison, and news sentiment - synthesizing an overall bullish, bearish, or neutral conviction.

**In progress / upcoming features:**

- Cryptocurrency analysis: Support for crypto tickers (e.g., BTC-USD, ETH-USD) with similar multi-agent sentiment workflow.
- Single-family home real estate analysis: The user enters a full property address; the system retrieves property data, comps, estimated value, rental potential, neighborhood trends, and generates an AI-powered investment report (buy/neutral/pass conviction for rental or flip strategies).

The app features a visually appealing UI, markdown-rendered insights, loading states, error handling, and PDF export.

## Instructions

### Running Locally

1. Navigate to the project root.
2. Create a `.env` file **in the `server` folder** with required variables (e.g., Groq API key – see `server/.env.example`).
3. Set up a Python virtual environment **in the `server` folder** (Python 3.12 recommended):

```
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
```

4. Install backend dependencies **(from the `server` folder)**:

```
pip install -r requirements.txt
```

5. Run the backend server:

```
uvicorn main:app --reload --port 8000
```

The API will run on http://localhost:8000.

6. In a separate terminal, navigate to the `client` folder (Angular app):

```
cd client
npm install
ng serve
```

The frontend will run on http://localhost:4200.

7. Open your browser to http://localhost:4200, enter a ticker like NVDA, select direction and duration, and generate a report.

   To test the API directly:

   ```
   curl -X POST "http://localhost:8000/api/research-equity" -H "Content-Type: application/json" -d '{"ticker": "NVDA", "trade_duration": "swing_trade", "trade_direction": "long"}'
   ```

### Running in Docker

This project uses a multi-stage Dockerfile to build the Angular frontend and serve it with the FastAPI backend in a single container.

To run the application locally with Docker, follow these steps:

1. Create a `.env` file in the project root with your required environment variables (e.g., Groq API Keys – see `server/.env.example` for details).
2. Ensure your local Docker daemon is running.
3. Build and run the container from the project root:

```
docker build -t investment-research-project .
docker run -p 8000:8000 --env-file .env investment-research-project
```

4. The application will be available at http://localhost:8000.

   To test the API directly:

   ```
   curl -X POST "http://localhost:8000/api/research-equity" -H "Content-Type: application/json" -d '{"ticker": "NVDA", "trade_duration": "swing_trade", "trade_direction": "long"}'
   ```

## Architecture

Conviction Insight uses a multi-agent LangGraph workflow to generate structured research reports. The graph validates the input, runs specialized agents in parallel, aggregates results, and iteratively refines the final output via an evaluator (up to 3 revisions for quality).

### Key Design Patterns

- **Tool-Use Agents**: Fetch structured data via yfinance (Fundamental, Technical, Macro)
- **Web RAG Agents**: Perform real-time research (News, Industry, Peer)
- **Stateful Graph Execution**: Parallel agent runs → aggregation → quality evaluation with optional revisions
- **Intelligent Caching**: Node-level TTLs (short for technicals, longer for macro/fundamentals)

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

### Stock Equity Research Agents

| Agent        | Focus                                  | Method                 |
| ------------ | -------------------------------------- | ---------------------- |
| Fundamentals | Financial statements, valuations       | yfinance tool calls    |
| Technical    | Price patterns, indicators (RSI, MACD) | yfinance + computation |
| Macro        | Economic indicators, rates             | Structured data        |
| Industry     | Sector trends, headwinds               | Web research           |
| Peer         | Competitor comparison                  | Web research           |
| News         | Recent headline and social sentiment   | Web research           |

After parallel execution, a **Sentiment Aggregator** synthesizes findings, and a **Sentiment Evaluator** enforces quality (up to 3 revisions).

(SEC Filings RAG agent in development)

## Optimizations

- Node-level caching in LangGraph (e.g., short TTL for technicals, longer for fundamentals/macro).
- Bulk yfinance downloads for fast price tables.
- Efficient state management with Angular Signals to avoid unnecessary re-renders.
- Custom markdown normalization and pdfmake parsing for clean PDF exports.

## Lessons Learned

Building Conviction Insight deepened my understanding of multi-agent AI systems with LangGraph, including state management, conditional routing, and caching for cost/speed. On the frontend, mastering Angular Signals, PrimeNG integration, and custom PDF generation improved my skills in reactive, performant UIs. Integrating real-time financial data while handling errors and loading states honed full-stack reliability.

## Improvements

- Add support for crypto tickers (already partially implemented with yfinance crypto endpoints).
- Implement real estate analysis for single-family home addresses (e.g., integrating property data APIs).
- Add user authentication and saved reports/history.
- Integrate observability tools like LangSmith for tracing agent executions.
