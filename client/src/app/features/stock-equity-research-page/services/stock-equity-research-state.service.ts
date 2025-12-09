import { computed, Injectable, signal } from '@angular/core';

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

@Injectable({
  providedIn: 'root',
})
export class StockEquityResearchStateService {
  // Private writable signals
  private readonly _request = signal<StockRequest | null>(null);
  private readonly _report = signal<StockReport | null>(null);
  private readonly _isLoading = signal<boolean>(false);
  private readonly _error = signal<string | null>(null);

  // Public read-only signals
  readonly request = this._request.asReadonly();
  readonly report = this._report.asReadonly();
  readonly isLoading = this._isLoading.asReadonly();
  readonly error = this._error.asReadonly();

  // Derived / computed state
  readonly ticker = computed(() => this._request()?.ticker.toUpperCase() ?? '');
  readonly direction = computed(() => this._request()?.direction ?? null);
  readonly duration = computed(() => this._request()?.duration ?? null);
  readonly hasReport = computed(() => this._report() !== null);
  readonly isIdle = computed(() => !this._isLoading() && !this._report() && !this._error());

  // Only way to change state
  generateReport(request: StockRequest): void {
    this._request.set({ ...request });
    this._report.set(null);
    this._isLoading.set(true);
    this._error.set(null);
  }

  completeWithReport(report: StockReport): void {
    this._report.set(report);
    this._isLoading.set(false);
  }

  failWithError(message: string): void {
    this._error.set(message);
    this._isLoading.set(false);
  }

  reset(): void {
    this._request.set(null);
    this._report.set(null);
    this._isLoading.set(false);
    this._error.set(null);
  }

  // Helpful for debugging or future analytics
  getCurrentStateSnapshot() {
    return {
      request: this._request(),
      hasReport: this.hasReport(),
      isLoading: this._isLoading(),
      error: this._error(),
      ticker: this.ticker(),
    };
  }
}
