import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { StocksState, StockReport, StockRequest } from '../state/stock-state';
import { finalize } from 'rxjs';
import { StockEquityResearchStateService } from './stock-equity-research-state.service';
import { environment } from '../../../../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class StockResearchService {
  private http = inject(HttpClient);
  private state = inject(StockEquityResearchStateService);

  private readonly baseUrl = environment.apiBaseUrl;

  generateReport(request: StockRequest) {
    console.log(request, 'REQUEST');
    this.state.generateReport(request); // update UI immediately
    // MOCK: Simulate API delay and return fake data
    setTimeout(() => {
      const mockReport: StockReport = {
        // {

        ticker: 'NVDA',

        sentiment_analysis: {
          fundamental:
            "[Valuation.OVERVALUED]\n\n* The P/E ratio of 43.32 is higher than the industry average\n* The price-to-book ratio of 35.78 indicates overvaluation\n* The current price of $175.02 is below the mean target price of $250.93, but the stock's high growth rate and strong financials may justify the current price\n\nConfidence: Confidence.MEDIUM",

          technical:
            '[Sentiment.BEARISH]\n\n* The RSI (45.05) is in neutral territory, indicating a balance between buyers and sellers\n* The Stochastic Oscillator (29.68) is also in neutral territory, suggesting a lack of strong momentum\n* The SMA 50 trend is -1, indicating the price is below the 50-day moving average\n* The MACD (-1.94) is below the signal line, indicating a bearish trend\n* The Bollinger Band position (2.64) is neutral, but the overall sentiment score (-0.33) leans towards a bearish outlook\n\nConfidence: Confidence.MEDIUM',

          macro:
            '[Sentiment.NEUTRAL]\n\n* The GDP growth rate has increased by 4.4 percentage points in the last quarter, ending on 2025-04-01\n* The inflation rate has been steadily increasing, with a year-over-year inflation rate of 1.66% as of 2025-09-01\n* Consumer sentiment has been declining, with a current value of 53.6 as of 2025-10-01\n\nConfidence: Confidence.MEDIUM',

          peer: "Error executing agent: Error code: 429 - {'error': {'message': 'Rate limit reached for model `openai/gpt-oss-120b` in organization `org_01katbxgdbee4r8x0av29ed14v` service tier `on_demand` on tokens per minute (TPM): Limit 8000, Used 5726, Requested 5683. Please try again in 25.5675s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'compound', 'code': 'rate_limit_exceeded'}}",

          industry:
            '**BULLISH**  \n* AI‑driven demand propels the global semiconductor market to grow ≈ 15 % in 2025, with memory sales up > 24 % and non‑memory (advanced‑node ICs) up ≈ 13 % driven by AI servers and GPUs【IDC, 2025‑10‑01】  \n* Tailwind: Explosive AI adoption fuels demand for Nvidia’s GPUs and high‑bandwidth memory, boosting NVDA’s revenue outlook; Headwind: Over‑reliance on AI could temper growth in 2026, risking a slowdown for AI‑centric chipmakers【Semiconductor Intelligence, 2025‑09‑15】  \n* Emerging pattern: Fabless/IP leaders (Nvidia, Broadcom) post strong revenue and net‑income growth, while traditional IDMs and equipment suppliers face contraction, accelerating industry consolidation【Infosys, 2025‑10‑20】\n\n**Confidence:** High',

          news: "Error executing agent: Error code: 429 - {'error': {'message': 'Rate limit reached for model `openai/gpt-oss-120b` in organization `org_01katbxgdbee4r8x0av29ed14v` service tier `on_demand` on tokens per minute (TPM): Limit 8000, Used 4986, Requested 3404. Please try again in 2.925s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'compound', 'code': 'rate_limit_exceeded'}}",
        },

        combined_sentiment:
          "**Summary of Research Findings:**\n- Fundamental: The stock is overvalued with a high P/E ratio of 43.32 and price-to-book ratio of 35.78. However, its strong financials and high growth rate may justify the current price. The current price of $175.02 is below the mean target price of $250.93.\n- Technical: The technical analysis indicates a bearish sentiment with the MACD below the signal line and the price below the 50-day moving average. The RSI and Stochastic Oscillator are in neutral territory.\n- Macro: The macro analysis is neutral, with increasing GDP growth and inflation rates, but declining consumer sentiment.\n- Industry: The industry analysis is bullish, driven by AI demand propelling the global semiconductor market to grow approximately 15% in 2025.\n- Peer: Unable to analyze due to error.\n- News: Unable to analyze due to error.\n\nConsensus and Divergence:\n- Consensus: There is a consensus among the fundamental and technical analyses that the stock may be overvalued and has a bearish outlook.\n- Divergence: The industry analysis diverges from the fundamental and technical analyses, indicating a bullish outlook due to AI-driven demand.\n\nWeighting of Perspectives:\n- Fundamental: 25% - The fundamental analysis is important for a swing trade, but the high growth rate and strong financials may justify the current price.\n- Industry: 30% - The industry analysis is crucial for understanding the demand drivers and growth potential.\n- Peer: 0% - Unable to analyze due to error.\n- News: 0% - Unable to analyze due to error.\n- Macro: 20% - The macro analysis is neutral and has a moderate impact on the trade.\n- Technical: 25% - The technical analysis is important for entry and exit points in a swing trade.\n\n**Overall Sentiment:** BEARISH\n\n**Conclusion:** The overall sentiment is bearish, driven by the technical analysis and fundamental overvaluation. However, the industry analysis presents a bullish case due to AI-driven demand. Considering the swing trade duration, the technical and fundamental analyses are prioritized. The trade direction is short, which aligns with the bearish sentiment. Despite the bullish industry outlook, the current overvaluation and bearish technicals suggest a short position. Nevertheless, the strong growth rate and AI-driven demand may limit the downside potential, and investors should closely monitor the stock's price and industry trends.",
      };
      this.state.completeWithReport(mockReport);
    }, 5000); // 2-second fake delay to see loading skeleton
  }
  //   return this.http
  //     .post<StockReport>(`${this.baseUrl}/research-equity`, request)
  //     .pipe(
  //       finalize(() => {
  //         // If request changed mid-flight, ignore stale response
  //         if (this.state.request()?.ticker !== request.ticker) return;
  //       }),
  //     )
  //     .subscribe({
  //       next: (report) => {
  //         this.state.completeWithReport(report);
  //         console.log(report, 'REPORT');
  //       },

  //       error: () => this.state.failWithError('Failed to generate report. Try again.'),
  //     });
  // }
}

// {

//     "ticker": "NVDA",

//     "sentiment_analysis": {

//         "fundamental": "[Valuation.OVERVALUED]\n\n* The P/E ratio of 43.32 is higher than the industry average\n* The price-to-book ratio of 35.78 indicates overvaluation\n* The current price of $175.02 is below the mean target price of $250.93, but the stock's high growth rate and strong financials may justify the current price\n\nConfidence: Confidence.MEDIUM",

//         "technical": "[Sentiment.BEARISH]\n\n* The RSI (45.05) is in neutral territory, indicating a balance between buyers and sellers\n* The Stochastic Oscillator (29.68) is also in neutral territory, suggesting a lack of strong momentum\n* The SMA 50 trend is -1, indicating the price is below the 50-day moving average\n* The MACD (-1.94) is below the signal line, indicating a bearish trend\n* The Bollinger Band position (2.64) is neutral, but the overall sentiment score (-0.33) leans towards a bearish outlook\n\nConfidence: Confidence.MEDIUM",

//         "macro": "[Sentiment.NEUTRAL]\n\n* The GDP growth rate has increased by 4.4 percentage points in the last quarter, ending on 2025-04-01\n* The inflation rate has been steadily increasing, with a year-over-year inflation rate of 1.66% as of 2025-09-01\n* Consumer sentiment has been declining, with a current value of 53.6 as of 2025-10-01\n\nConfidence: Confidence.MEDIUM",

//         "peer": "Error executing agent: Error code: 429 - {'error': {'message': 'Rate limit reached for model `openai/gpt-oss-120b` in organization `org_01katbxgdbee4r8x0av29ed14v` service tier `on_demand` on tokens per minute (TPM): Limit 8000, Used 5726, Requested 5683. Please try again in 25.5675s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'compound', 'code': 'rate_limit_exceeded'}}",

//         "industry": "**BULLISH**  \n* AI‑driven demand propels the global semiconductor market to grow ≈ 15 % in 2025, with memory sales up > 24 % and non‑memory (advanced‑node ICs) up ≈ 13 % driven by AI servers and GPUs【IDC, 2025‑10‑01】  \n* Tailwind: Explosive AI adoption fuels demand for Nvidia’s GPUs and high‑bandwidth memory, boosting NVDA’s revenue outlook; Headwind: Over‑reliance on AI could temper growth in 2026, risking a slowdown for AI‑centric chipmakers【Semiconductor Intelligence, 2025‑09‑15】  \n* Emerging pattern: Fabless/IP leaders (Nvidia, Broadcom) post strong revenue and net‑income growth, while traditional IDMs and equipment suppliers face contraction, accelerating industry consolidation【Infosys, 2025‑10‑20】\n\n**Confidence:** High",

//         "news": "Error executing agent: Error code: 429 - {'error': {'message': 'Rate limit reached for model `openai/gpt-oss-120b` in organization `org_01katbxgdbee4r8x0av29ed14v` service tier `on_demand` on tokens per minute (TPM): Limit 8000, Used 4986, Requested 3404. Please try again in 2.925s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'compound', 'code': 'rate_limit_exceeded'}}"

//     },

//     "combined_sentiment": "**Summary of Research Findings:**\n- Fundamental: The stock is overvalued with a high P/E ratio of 43.32 and price-to-book ratio of 35.78. However, its strong financials and high growth rate may justify the current price. The current price of $175.02 is below the mean target price of $250.93.\n- Technical: The technical analysis indicates a bearish sentiment with the MACD below the signal line and the price below the 50-day moving average. The RSI and Stochastic Oscillator are in neutral territory.\n- Macro: The macro analysis is neutral, with increasing GDP growth and inflation rates, but declining consumer sentiment.\n- Industry: The industry analysis is bullish, driven by AI demand propelling the global semiconductor market to grow approximately 15% in 2025.\n- Peer: Unable to analyze due to error.\n- News: Unable to analyze due to error.\n\nConsensus and Divergence:\n- Consensus: There is a consensus among the fundamental and technical analyses that the stock may be overvalued and has a bearish outlook.\n- Divergence: The industry analysis diverges from the fundamental and technical analyses, indicating a bullish outlook due to AI-driven demand.\n\nWeighting of Perspectives:\n- Fundamental: 25% - The fundamental analysis is important for a swing trade, but the high growth rate and strong financials may justify the current price.\n- Industry: 30% - The industry analysis is crucial for understanding the demand drivers and growth potential.\n- Peer: 0% - Unable to analyze due to error.\n- News: 0% - Unable to analyze due to error.\n- Macro: 20% - The macro analysis is neutral and has a moderate impact on the trade.\n- Technical: 25% - The technical analysis is important for entry and exit points in a swing trade.\n\n**Overall Sentiment:** BEARISH\n\n**Conclusion:** The overall sentiment is bearish, driven by the technical analysis and fundamental overvaluation. However, the industry analysis presents a bullish case due to AI-driven demand. Considering the swing trade duration, the technical and fundamental analyses are prioritized. The trade direction is short, which aligns with the bearish sentiment. Despite the bullish industry outlook, the current overvaluation and bearish technicals suggest a short position. Nevertheless, the strong growth rate and AI-driven demand may limit the downside potential, and investors should closely monitor the stock's price and industry trends."

// }
