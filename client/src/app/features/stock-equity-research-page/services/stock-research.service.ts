// Angular
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';

// Libraries
import { finalize } from 'rxjs';

// Application
import { StockReport, StockRequest } from './stock-equity-research-state.service';
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
    this.state.generateReport(request);

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
