import { computed, Injectable, signal } from '@angular/core';

export interface CryptoRequest {
  ticker: string;
  direction: 'long' | 'short';
  duration: string;
}

export interface CryptoReport {
  ticker: string;
  sentiment_analysis: {
    technical: string;
    macro: string;
    news: string;
    peer: string;
  };
  combined_sentiment: string;
}

@Injectable({
  providedIn: 'root',
})
export class CryptoResearchStateService {
   // Private writable signals
    private readonly _request = signal<CryptoRequest | null>(null);
    private readonly _report = signal<CryptoReport | null>(null);
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
    generateReport(request: CryptoRequest): void {
      this._request.set({ ...request });
      this._report.set(null);
      this._isLoading.set(true);
      this._error.set(null);
    }
  
    completeWithReport(report: CryptoReport): void {
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
