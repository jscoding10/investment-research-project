import { computed, Injectable, signal } from '@angular/core';

import { RealEstateReport, RealEstateRequest } from '../types';

@Injectable({
  providedIn: 'root',
})
export class RealEstateResearchStateService {
  // Private writable signals
  private readonly _request = signal<RealEstateRequest | null>(null);
  private readonly _report = signal<RealEstateReport | null>(null);
  private readonly _isLoading = signal<boolean>(false);
  private readonly _error = signal<string | null>(null);

  // Public read-only signals
  readonly request = this._request.asReadonly();
  readonly report = this._report.asReadonly();
  readonly isLoading = this._isLoading.asReadonly();
  readonly error = this._error.asReadonly();

  // Derived / computed state
  readonly address = computed(() => this._report()?.address ?? this._request()?.address ?? '');
  readonly purchasePrice = computed(() => this._request()?.purchase_price ?? null);
  readonly downPaymentPct = computed(() => this._request()?.down_payment_pct ?? null);
  readonly loanTermYears = computed(() => this._request()?.loan_term_years ?? null);
  readonly interestRate = computed(() => this._request()?.interest_rate ?? null);
  readonly estimatedRent = computed(() => this._request()?.estimated_rent ?? null);
  readonly timeHorizonYears = computed(() => this._request()?.time_horizon_years ?? null);
  readonly hasReport = computed(() => this._report() !== null);
  readonly isIdle = computed(() => !this._isLoading() && !this._report() && !this._error());

  // Only way to change state
  generateReport(request: RealEstateRequest): void {
    this._request.set({ ...request });
    this._report.set(null);
    this._isLoading.set(true);
    this._error.set(null);
  }

  completeWithReport(report: RealEstateReport): void {
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
      address: this.address(),
    };
  }
}
