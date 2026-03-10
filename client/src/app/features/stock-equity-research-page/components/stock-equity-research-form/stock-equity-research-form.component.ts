import { Component, inject, OnDestroy, OnInit, signal } from '@angular/core';
import { FormBuilder, FormControl, Validators } from '@angular/forms';
import { ReactiveFormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

import { Subject, takeUntil } from 'rxjs';
import { debounceTime } from 'rxjs/operators';

import { AutoCompleteModule } from 'primeng/autocomplete';
import { InputTextModule } from 'primeng/inputtext';
import { SelectModule } from 'primeng/select';

import { StockRequest, StockSuggestion } from '../../types';
import { FormFieldConfig, TradeDirectionOptions, TradeDurationOptions } from '../../../../types';

import { StockResearchService } from '../../services/stock-research.service';

const stockEquityFormConfig: FormFieldConfig[] = [
  {
    name: 'ticker',
    type: 'autocomplete',
    validators: [Validators.required],
  },
  {
    name: 'tradeDirection',
    type: 'select',
    validators: [Validators.required],
  },
  {
    name: 'tradeDuration',
    type: 'select',
    validators: [Validators.required],
  },
];

@Component({
  selector: 'app-stock-equity-research-form',
  imports: [SelectModule, InputTextModule, AutoCompleteModule, ReactiveFormsModule],
  templateUrl: './stock-equity-research-form.component.html',
  styleUrl: './stock-equity-research-form.component.css',
})
export class StockEquityResearchFormComponent implements OnInit, OnDestroy {
  private stockResearchService = inject(StockResearchService);
  private http = inject(HttpClient);
  private fb = inject(FormBuilder);

  stockSuggestions: StockSuggestion[] = [];
  // Signal to determine whether form is submitted or not
  submitted = signal(false);

  // Initialize form builder group to empty object
  stockEquityResearchForm = this.fb.group<Record<string, FormControl>>({});

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
    this.buildForm(stockEquityFormConfig);

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

  private buildForm(config: FormFieldConfig[]) {
    config.forEach((field) => {
      this.stockEquityResearchForm.addControl(field.name, this.fb.control(null, field.validators ?? []));
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

    const raw = this.stockEquityResearchForm.getRawValue();

    const request: StockRequest = {
      ticker: raw['ticker'],
      trade_direction: raw['tradeDirection'],
      trade_duration: raw['tradeDuration'],
    };

    this.stockResearchService.generateReport(request);

    this.stockEquityResearchForm.reset();
  }

  // Method to determine if form control is invalid
  isFieldInvalid(controlName: string): boolean | undefined {
    const control = this.stockEquityResearchForm.get(controlName);
    return control?.invalid && (control.touched || this.submitted());
  }
}
