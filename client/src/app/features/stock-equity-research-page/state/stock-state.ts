// src/app/features/stocks/stocks.state.ts
import { computed, Injectable, signal, WritableSignal } from '@angular/core';

export interface StockRequest {
  ticker: string;
  direction: 'long' | 'short';
  duration: string;
}

export interface StockReport {
  ticker: string;
  sentiment_analysis: {
    fundamental: string;
    technical: string;
    macro: string;
    industry: string;
    news: string;
    peer: string;
  };
  combined_sentiment: string;
}

@Injectable({ providedIn: 'root' })
export class StocksState {
  // ── Private writable signals  ──
  private request: WritableSignal<StockRequest | null> = signal(null);
  private _report: WritableSignal<StockReport | null> = signal(null);
  private _loading: WritableSignal<boolean> = signal(false);
  private _error: WritableSignal<string | null> = signal(null);

  // ── Public read-only signals  ──
  readonly currentRequest = this.request.asReadonly();
  readonly report = this._report.asReadonly();
  readonly isLoading = this._loading.asReadonly();
  readonly error = this._error.asReadonly();

  readonly ticker = computed(() => this.request()?.ticker.toUpperCase() ?? '');
  readonly hasReport = computed(() => this.report() !== null);

  // ── Intent methods  ──
  generateReport(request: StockRequest) {
    this.request.set(request);
    this._report.set(null);
    this._loading.set(true);
    this._error.set(null);
  }

  completeWithReport(report: StockReport) {
    this._report.set(report);
    this._loading.set(false);
  }

  failWithError(message: string) {
    this._error.set(message);
    this._loading.set(false);
  }

  reset() {
    this.request.set(null);
    this._report.set(null);
    this._loading.set(false);
    this._error.set(null);
  }
}
