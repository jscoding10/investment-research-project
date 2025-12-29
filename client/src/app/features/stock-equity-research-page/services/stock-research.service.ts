import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { StockReport, StockRequest } from '../state/stock-state';
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
    // setTimeout(() => {
    //   const mockReport: StockReport = {
    //     ticker: request.ticker.toUpperCase(),
    //     sentiment_analysis: {
    //       fundamental: `UNDERVALUED\n\n* P/E ratio of 44.34 is reasonable given 65% revenue growth, resulting in PEG of approximately 0.68.\n* Exceptional ROE of 99.24% and ROA of 70.40% indicate strong profitability.\n* Low debt-to-equity ratio of 0.09 and high current ratio of 4.47 show excellent financial health.\n\nConfidence: High`,
    //       technical: `NEUTRAL\n\n* RSI at 58.71 indicates neutral momentum.\n* Price below 20-day (184.75) and 50-day (184.34) moving averages, signaling short-term weakness.\n* MACD shows no strong crossover, maintaining neutral stance.\n* Bollinger Bands have price in the middle band, no extreme volatility.\n* Long-term trend remains bullish as price above 200-day MA.\n\nConfidence: Medium`,
    //       macro: `BULLISH\n\n* GDP growth at 2.8% annualized in Q3 2024 supports economic expansion.\n* CPI inflation at 2.7% in November 2024 indicates cooling prices, nearing Fed target.\n* Consumer sentiment improving, with potential rate cuts boosting equity markets.\n\nConfidence: High`,
    //       industry: `POSITIVE\n\n* Semiconductor market driven by AI, expected 15% growth in 2025. [bloomberg.com, Nov 15, 2025]\n* Nvidia leads in GPU, b competition from AMD and Huawei increasing. [reuters.com, Dec 4, 2025]\n* Tailwinds: data center boom; Headwinds: geopolitical tensions. [cnbc.com, Nov 25, 2025]\n\nConfidence: High`,
    //       news: `BULLISH\n\n* Nvidia's cash pile enables strategic investments, like in OpenAI. [cnbc.com, Dec 4, 2025]\n* Strong AI demand continues, with high margins. [wsj.com, Dec 3, 2025]\n* Chinese rivals emerging, b Nvidia's tech lead persists. [cnbc.com, Dec 5, 2025]\n\nConfidence: Medium`,
    //     },
    //     combined_sentiment: `Summary of Research Findings:\n- Fundamental: NVDA is undervalued based on a PEG ratio of 0.68 driven by 65% revenue growth, with exceptional profitability metrics like 99.24% ROE and 70.40% ROA, alongside a strong balance sheet featuring low debt and high liquidity.\n- Technical: The stock shows neutral momentum with an RSI of 58.71, short-term weakness as price sits below key moving averages, b maintains a long-term bullish trend above the 200-day MA.\n- Macro: Bullish conditions prevail with 2.8% GDP growth in Q3 2024 and cooling inflation at 2.7% in November, potentially leading to supportive rate cuts.\n- Industry: Positive outlook due to AI-fueled 15% sector growth in 2025 and data center expansion, though tempered by increasing competition and geopolitical risks.\n- News: Bullish sentiment from robust AI demand, high margins, and strategic investments, despite emerging Chinese competitors.\n\nConsensus and Divergence:\n- Consensus: Strong growth prospects, profitability, and AI-driven tailwinds across fundamental, macro, industry, and news analyses.\n- Divergence: Technical analysis indicates short-term neutrality and weakness, contrasting with the positive long-term views from other perspectives.\n\nWeighting of Perspectives:\n- Fundamental 30% high confidence in core metrics and valuation.\n- Industry 25% critical for tech sector dynamics and growth drivers.\n- News 20% reflects recent events influencing market sentiment.\n- Macro 15% provides supportive broader context.\n- Technical 10% focused on short-term signals, less impactful for long-term thesis.\n\nOverall Sentiment: BEARISH\n\nConclusion: NVDA's undervalued position, fueled by explosive AI growth and strong financial health, combined with favorable macro and industry tailwinds, underpins a bullish investment thesis. Recent news reinforces demand strength despite competition. While technicals signal short-term caution, the overall opportunity favors long-term investors, acknowledging geopolitical uncertainties.`,
    //   };
    //   this.state.completeWithReport(mockReport);
    // }, 5000); // 2-second fake delay to see loading skeleton

    return this.http
      .post<StockReport>(`${this.baseUrl}/research-equity`, request)
      .pipe(
        finalize(() => {
          // If request changed mid-flight, ignore stale response
          if (this.state.request()?.ticker !== request.ticker) return;
        }),
      )
      .subscribe({
        next: (report) => {
          this.state.completeWithReport(report);
        },

        error: (err: any) => {
          let errorMsg = '';

          // Handle FastAPI validation errors
          if (err.error && typeof err.error === 'object' && err.error.detail) {
            if (typeof err.error.detail === 'string') {
              errorMsg = err.error.detail;
            } else if (Array.isArray(err.error.detail)) {
              // Sometimes FastAPI returns an array of errors (e.g., pydantic validation)
              errorMsg = err.error.detail.map((d: any) => d.msg || d).join('; ');
            }
          }
          // Fallback for network errors, timeout, etc.
          else if (err.message) {
            errorMsg = `Network error: ${err.message}`;
          }
          // Fallback MEssage
          else {
            errorMsg = 'An unexpected error occurred. Failed to generate report. Please try again.';
          }

          this.state.failWithError(errorMsg);
        },
      });
  }
}
