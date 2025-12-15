import { Component, inject, OnInit, signal } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';

import { SelectModule } from 'primeng/select';
import { InputTextModule } from 'primeng/inputtext';
import { ReactiveFormsModule } from '@angular/forms';
import { Subject, takeUntil } from 'rxjs';
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

@Component({
  selector: 'app-stock-equity-research-form',
  imports: [SelectModule, InputTextModule, ReactiveFormsModule],
  templateUrl: './stock-equity-research-form.component.html',
  styleUrl: './stock-equity-research-form.component.css',
})
export class StockEquityResearchFormComponent implements OnInit {
  // generateReport = output<StockRequest>();

  private stockResearchService = inject(StockResearchService);

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

  // Array of form control names
  formControls = ['ticker', 'trade_direction', 'trade_duration'];

  // Signal to determine whether form is submitted or not
  submitted = signal(false);

  // Emits a signal when the component is being destroyed.
  // Used with takeUntil() to automatically unsubscribe from all Observables.
  private destroy$ = new Subject<void>();

  // Initialize form group to empty object
  stockEquityResearchForm = new FormGroup({});

  isLoading = false;

  ngOnInit() {
    // Populate form group
    this.makeForm();

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

  onSubmit(): void {
    this.submitted.set(true);

    if (this.stockEquityResearchForm.invalid) {
      this.stockEquityResearchForm.markAllAsTouched();
      return;
    }

    const request = this.stockEquityResearchForm.getRawValue() as StockRequest;
    this.stockResearchService.generateReport(request);

    console.log('Form submitted successfully:', this.stockEquityResearchForm.getRawValue());
    this.stockEquityResearchForm.reset();
  }

  // Method to determine if form control is invalid
  isFieldInvalid(controlName: string): boolean | undefined {
    const control = this.stockEquityResearchForm.get(controlName);
    return control?.invalid && (control.touched || this.submitted());
  }
}
