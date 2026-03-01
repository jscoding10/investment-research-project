// Angular
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';

// Libraries
import { finalize } from 'rxjs';

// Application
import { RealEstateReport, RealEstateRequest } from './real-estate-research-state.service';
import { RealEstateResearchStateService } from './real-estate-research-state.service';
import { environment } from '../../../../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class RealEstateResearchService {
  private http = inject(HttpClient);
  private state = inject(RealEstateResearchStateService);

  private readonly baseUrl = environment.apiBaseUrl;

  generateReport(request: RealEstateRequest) {
    this.state.generateReport(request);

    return this.http
      .post<RealEstateReport>(`${this.baseUrl}/research-real-estate`, request)
      .pipe(
        finalize(() => {
          // If request changed mid-flight, ignore stale response
          if (this.state.request()?.address !== request.address) return;
        }),
      )
      .subscribe({
        next: (report) => this.state.completeWithReport(report),
        error: (err: any) => {
          let errorMsg = '';

          // Handle FastAPI validation errors
          if (err.error && typeof err.error === 'object' && err.error.detail) {
            errorMsg =
              typeof err.error.detail === 'string'
                ? // Sometimes FastAPI returns an array of errors (e.g., pydantic validation)
                err.error.detail
                : Array.isArray(err.error.detail)
                  ? err.error.detail.map((d: any) => d.msg || d).join('; ')
                  : 'Validation error';
          } else if (err.message) {
            // Fallback for network errors, timeout, etc.
            errorMsg = `Network error: ${err.message}`;
            // Fallback Message
          } else {
            errorMsg = 'An unexpected error occurred. Please try again.';
          }
          this.state.failWithError(errorMsg);
        },
      });
  }
}
