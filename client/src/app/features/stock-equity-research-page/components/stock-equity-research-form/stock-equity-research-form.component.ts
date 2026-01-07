import { Component, inject, OnInit, signal } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { ReactiveFormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

import { Subject, takeUntil } from 'rxjs';
import { debounceTime } from 'rxjs/operators';

import { SelectModule } from 'primeng/select';
import { InputTextModule } from 'primeng/inputtext';
import { AutoCompleteModule } from 'primeng/autocomplete';

import { StockResearchService } from '../../services/stock-research.service';

interface TradeDirectionOptions {
  name: string;
  value: string;
}

interface TradeDurationOptions {
  name: string;
  value: string;
}
export interface StockRequest {
  ticker: string;
  direction: 'long' | 'short';
  duration: string;
}

interface StockSuggestion {
  symbol: string;
  name: string;
}

@Component({
  selector: 'app-stock-equity-research-form',
  imports: [SelectModule, InputTextModule, AutoCompleteModule, ReactiveFormsModule],
  templateUrl: './stock-equity-research-form.component.html',
  styleUrl: './stock-equity-research-form.component.css',
})
export class StockEquityResearchFormComponent implements OnInit {
  private stockResearchService = inject(StockResearchService);
  private http = inject(HttpClient);

  stockSuggestions: StockSuggestion[] = [];
  // Signal to determine whether form is submitted or not
  submitted = signal(false);

  // Initialize form group to empty object
  stockEquityResearchForm = new FormGroup({});
  // Array of form control names
  formControls = ['ticker', 'trade_direction', 'trade_duration'];

  // PrimeNg Trade Direction Select Options
  tradeDirectionOptions: Array<TradeDirectionOptions> = [
    { name: 'Long', value: 'long' },
    { name: 'Short', value: 'short' },
  ];

  // PrimeNg Trade Duration Select Options
  tradeDurationOptions: Array<TradeDurationOptions> = [
    { name: 'Day Trade', value: 'day_trade' },
    { name: 'Swing Trade', value: 'swing_trade' },
    { name: 'Position Trade', value: 'position_trade' },
  ];

  private searchTerms = new Subject<string>();
  // Emits a signal when the component is being destroyed.
  // Used with takeUntil() to automatically unsubscribe from all Observables.
  private destroy$ = new Subject<void>();

  ngOnInit() {
    // Populate form group
    this.makeForm();

    this.searchTerms.pipe(debounceTime(500), takeUntil(this.destroy$)).subscribe((query) => {
      this.performSearch(query);
    });

    // Subscribe to form value changes and auto-unsubscribe when destroy$ emits.
    // Prevents memory leaks from long-lived subscriptions.
    this.stockEquityResearchForm.valueChanges.pipe(takeUntil(this.destroy$)).subscribe(() => {
      if (this.submitted()) this.submitted.set(false);
    });
  }

  // Trigger all takeUntil() subscriptions to complete and clean up the destroy$ Subject
  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  makeForm() {
    // Loop through array and generate form controls - all fields are required in this case
    this.formControls.map((control) => {
      this.stockEquityResearchForm.addControl(control, new FormControl('', Validators.required));
    });
  }

  search(event: { query: string }) {
    const query = event.query.trim().toUpperCase();

    if (!query) {
      this.stockSuggestions = [];
      return;
    }

    // Push query into the observable stream (will be debounced)
    this.searchTerms.next(query);
  }

  private performSearch(query: string) {
    this.http.get<StockSuggestion[]>(`/api/ticker-search?q=${encodeURIComponent(query)}`).subscribe({
      next: (data) => {
        this.stockSuggestions = [];
        this.stockSuggestions = data;
      },
      error: (err) => {
        console.error('Ticker search failed:', err);
        this.stockSuggestions = [];
      },
    });
  }

  onSubmit(): void {
    this.submitted.set(true);

    if (this.stockEquityResearchForm.invalid) {
      this.stockEquityResearchForm.markAllAsTouched();
      return;
    }

    const request = this.stockEquityResearchForm.getRawValue() as StockRequest;
    this.stockResearchService.generateReport(request);

    this.stockEquityResearchForm.reset();
  }

  // Method to determine if form control is invalid
  isFieldInvalid(controlName: string): boolean | undefined {
    const control = this.stockEquityResearchForm.get(controlName);
    return control?.invalid && (control.touched || this.submitted());
  }
}
