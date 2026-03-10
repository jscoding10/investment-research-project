import { Component, inject, OnDestroy, OnInit, signal } from '@angular/core';
import { FormBuilder, FormControl, Validators } from '@angular/forms';
import { ReactiveFormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

import { Subject, takeUntil } from 'rxjs';
import { debounceTime } from 'rxjs/operators';

import { AutoCompleteModule, AutoCompleteSelectEvent } from 'primeng/autocomplete';
import { InputNumberModule } from 'primeng/inputnumber';
import { InputTextModule } from 'primeng/inputtext';

import { AddressSuggestion, RealEstateRequest } from '../../types';
import { FormFieldConfig } from '../../../../types';

import { RealEstateResearchService } from '../../services/real-estate-research.service';

const realEstateFormConfig: FormFieldConfig[] = [
  {
    name: 'addressSearch',
    type: 'text',
    validators: [],
  },
  {
    name: 'streetAddress',
    type: 'text',
    validators: [Validators.required],
  },
  {
    name: 'city',
    type: 'text',
    validators: [Validators.required],
  },
  {
    name: 'state',
    type: 'text',
    validators: [Validators.required],
  },
  {
    name: 'zipCode',
    type: 'text',
    validators: [Validators.required],
  },
  {
    name: 'purchasePrice',
    type: 'number',
    validators: [],
  },
  {
    name: 'downPaymentPercent',
    type: 'number',
    validators: [Validators.required],
  },
  {
    name: 'loanTermYears',
    type: 'number',
    validators: [Validators.required],
  },
  {
    name: 'interestRate', // Add in init to call current rate
    type: 'number',
    validators: [Validators.required],
  },
  {
    name: 'estimatedRent',
    type: 'number',
    validators: [],
  },
  {
    name: 'timeHorizonYears',
    type: 'number',
    validators: [],
  },
];

@Component({
  selector: 'app-real-estate-research-form',
  imports: [InputTextModule, InputNumberModule, AutoCompleteModule, ReactiveFormsModule],
  templateUrl: './real-estate-research-form.component.html',
  styleUrl: './real-estate-research-form.component.css',
})
export class RealEstateResearchFormComponent implements OnInit, OnDestroy {
  private realEstateService = inject(RealEstateResearchService);
  private http = inject(HttpClient);
  private fb = inject(FormBuilder);

  submitted = signal(false);

  // Initialize form builder group to empty object
  realEstateForm = this.fb.group<Record<string, FormControl>>({});

  addressSuggestions: AddressSuggestion[] = [];

  private searchTerms = new Subject<string>();
  private destroy$ = new Subject<void>();

  ngOnInit() {
    this.buildForm(realEstateFormConfig);

    this.realEstateForm.patchValue({
      downPaymentPercent: 20,
      // Make dropdown
      loanTermYears: 30,
      // Update to call market value
      interestRate: 6.5,
    });

    this.realEstateForm.valueChanges.pipe(takeUntil(this.destroy$)).subscribe(() => {
      if (this.submitted()) this.submitted.set(false);
    });

    this.searchTerms.pipe(debounceTime(500), takeUntil(this.destroy$)).subscribe((query) => {
      this.performSearch(query);
    });
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private buildForm(config: FormFieldConfig[]) {
    config.forEach((field) => {
      this.realEstateForm.addControl(field.name, this.fb.control(null, field.validators ?? []));
    });
  }

  search(event: { query: string }) {
    const query = event.query.trim();

    if (!query) {
      this.addressSuggestions = [];
      return;
    }

    this.searchTerms.next(query);
  }

  private performSearch(query: string) {
    this.http.get<AddressSuggestion[]>(`/api/address-search?q=${encodeURIComponent(query)}`).subscribe({
      next: (data) => {
        this.addressSuggestions = data;
      },
      error: (err) => {
        console.error('Address search failed:', err);
        this.addressSuggestions = [];
      },
    });
  }

  onAddressSelected(event: AutoCompleteSelectEvent) {
    const selected: AddressSuggestion = event.value;

    let street = selected.street?.trim() || '';
    if (selected.secondary?.trim()) {
      street += ` ${selected.secondary.trim()}`;
    }

    this.realEstateForm.patchValue({
      streetAddress: street,
      city: selected.city?.trim() || '',
      state: selected.state?.trim() || '',
      zipCode: selected.zipcode?.trim() || '',
    });
  }

  onSubmit(): void {
    this.submitted.set(true);
    if (this.realEstateForm.invalid) {
      this.realEstateForm.markAllAsTouched();
      return;
    }

    // Get raw values with proper typing (string | number | null)
    const raw = this.realEstateForm.getRawValue();

    // Build properly formatted address with commas
    const addressParts: string[] = [];

    if (raw['streetAddress']?.trim()) {
      addressParts.push(raw['streetAddress'].trim());
    }
    if (raw['city']?.trim()) {
      addressParts.push(raw['city'].trim());
    }
    if (raw['state']?.trim()) {
      addressParts.push(raw['state'].trim());
    }
    if (raw['zipCode']?.trim()) {
      addressParts.push(raw['zipCode'].trim());
    }

    const address = addressParts.join(', ');

    // Format field names for Python backend
    const request: RealEstateRequest = {
      address,
      purchase_price: Number(raw['purchasePrice'] ?? 0),
      down_payment_pct: Number(raw['downPaymentPercent'] ?? 0),
      loan_term_years: Number(raw['loanTermYears'] ?? 0),
      interest_rate: Number(raw['interestRate'] ?? 0),
      estimated_rent: Number(raw['estimatedRent'] ?? 0),
      time_horizon_years: Number(raw['timeHorizonYears'] ?? 0),
    };

    this.realEstateService.generateReport(request);
    this.realEstateForm.reset();
  }

  isFieldInvalid(controlName: string): boolean | undefined {
    const control = this.realEstateForm.get(controlName);
    return control?.invalid && (control.touched || this.submitted());
  }
}
