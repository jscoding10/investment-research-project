import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MarkdownModule } from 'ngx-markdown';
import { StockReport } from '../../state/stock-state';
import { StockEquityResearchStateService } from '../../services/stock-equity-research-state.service';

@Component({
  selector: 'app-stock-equity-research-report',
  imports: [CommonModule, MarkdownModule],
  templateUrl: './stock-equity-research-report.component.html',
  styleUrl: './stock-equity-research-report.component.css',
})
export class StockEquityResearchReportComponent {
  private state = inject(StockEquityResearchStateService);

  report = this.state.report;
  isLoading = this.state.isLoading;
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
    if (text.includes('BULLISH')) return 'BULLISH';
    if (text.includes('BEARISH')) return 'BEARISH';

    return 'NEUTRAL';
  }
}
