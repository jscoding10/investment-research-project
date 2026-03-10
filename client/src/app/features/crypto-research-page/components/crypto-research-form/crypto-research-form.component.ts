import { Component, inject, OnDestroy, OnInit, signal } from '@angular/core';
import { FormBuilder, FormControl, Validators } from '@angular/forms';
import { ReactiveFormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

import { Subject, takeUntil } from 'rxjs';
import { debounceTime } from 'rxjs/operators';

import { AutoCompleteModule } from 'primeng/autocomplete';
import { InputTextModule } from 'primeng/inputtext';
import { SelectModule } from 'primeng/select';

import { CryptoRequest, CryptoSuggestion } from '../../types';
import { FormFieldConfig, TradeDirectionOptions, TradeDurationOptions } from '../../../../types';

import { CryptoResearchService } from '../../services/crypto-research.service';

const cryptoFormConfig: FormFieldConfig[] = [
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
  selector: 'app-crypto-research-form',
  imports: [SelectModule, InputTextModule, AutoCompleteModule, ReactiveFormsModule],
  templateUrl: './crypto-research-form.component.html',
  styleUrl: './crypto-research-form.component.css',
})
export class CryptoResearchFormComponent implements OnInit, OnDestroy {
  private cryptoResearchService = inject(CryptoResearchService);
  private http = inject(HttpClient);
  private fb = inject(FormBuilder);

  cryptoSuggestions: CryptoSuggestion[] = [];
  // Signal to determine whether form is submitted or not
  submitted = signal(false);

  // Initialize form builder group to empty object
  cryptoResearchForm = this.fb.group<Record<string, FormControl>>({});

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
    this.buildForm(cryptoFormConfig);

    this.searchTerms.pipe(debounceTime(500), takeUntil(this.destroy$)).subscribe((query) => {
      this.performSearch(query);
    });

    // Subscribe to form value changes and auto-unsubscribe when destroy$ emits.
    // Prevents memory leaks from long-lived subscriptions.
    this.cryptoResearchForm.valueChanges.pipe(takeUntil(this.destroy$)).subscribe(() => {
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
      this.cryptoResearchForm.addControl(field.name, this.fb.control(null, field.validators ?? []));
    });
  }

  search(event: { query: string }) {
    const query = event.query.trim().toUpperCase();

    if (!query) {
      this.cryptoSuggestions = [];
      return;
    }

    // Push query into the observable stream (will be debounced)
    this.searchTerms.next(query);
  }

  private performSearch(query: string) {
    this.http.get<CryptoSuggestion[]>(`/api/crypto-ticker-search?q=${encodeURIComponent(query)}`).subscribe({
      next: (data) => {
        this.cryptoSuggestions = data;
      },
      error: (err) => {
        console.error('Crypto ticker search failed:', err);
        this.cryptoSuggestions = [];
      },
    });
  }

  onSubmit(): void {
    this.submitted.set(true);

    if (this.cryptoResearchForm.invalid) {
      this.cryptoResearchForm.markAllAsTouched();
      return;
    }

    const raw = this.cryptoResearchForm.getRawValue();

    const request: CryptoRequest = {
      ticker: raw['ticker'],
      trade_direction: raw['tradeDirection'],
      trade_duration: raw['tradeDuration'],
    };

    this.cryptoResearchService.generateReport(request);

    this.cryptoResearchForm.reset();
  }

  // Method to determine if form control is invalid
  isFieldInvalid(controlName: string): boolean | undefined {
    const control = this.cryptoResearchForm.get(controlName);
    return control?.invalid && (control.touched || this.submitted());
  }
}
