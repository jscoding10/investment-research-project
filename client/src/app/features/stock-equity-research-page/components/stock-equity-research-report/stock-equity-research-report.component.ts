import { Component, effect, inject, Input, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SimpleMarkdownComponent } from '../simple-markdown/simple-markdown.component';
import { StocksState } from '../../state/stock-state';
import { StockReport } from '../../state/stock-state';
import { StockEquityResearchStateService } from '../../services/stock-equity-research-state.service';

@Component({
  selector: 'app-stock-equity-research-report',
  imports: [CommonModule, SimpleMarkdownComponent],
  templateUrl: './stock-equity-research-report.component.html',
  styleUrl: './stock-equity-research-report.component.css',
})
export class StockEquityResearchReportComponent {
  private state = inject(StockEquityResearchStateService);

  // report = this.state.report;
  report = this.state.report; // read-only signal
  isLoading = this.state.isLoading; // read-only signal
  ticker = this.state.ticker;
  error = this.state.error;

  getOverallReport(report: StockReport | null): string {
    if (!report) return 'NEUTRAL';
    const match = report.combined_sentiment.match(/Overall Sentiment: (\w+)/);
    return match ? (match[1] as 'BULLISH' | 'BEARISH' | 'NEUTRAL') : 'NO REPORT';
  }

  getOverallSentiment(report: StockReport): 'BULLISH' | 'BEARISH' | 'NEUTRAL' {
    const text = report.combined_sentiment.toUpperCase();

    if (text.includes('OVERALL SENTIMENT: BULLISH') || text.includes('**OVERALL SENTIMENT:** BULLISH')) {
      return 'BULLISH';
    }
    if (text.includes('OVERALL SENTIMENT: BEARISH') || text.includes('**OVERALL SENTIMENT:** BEARISH')) {
      return 'BEARISH';
    }
    // Fallback: look for the word right before the final conclusion
    if (text.includes('BULLISH')) return 'BULLISH';
    if (text.includes('BEARISH')) return 'BEARISH';

    return 'NEUTRAL';
  }
}
