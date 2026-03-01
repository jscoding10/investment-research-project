// Angular
import { Component, inject, OnDestroy, OnInit, signal } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { ReactiveFormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

// Libraries
import { Subject, takeUntil } from 'rxjs';
import { debounceTime } from 'rxjs/operators';

// PrimeNG
import { InputTextModule } from 'primeng/inputtext';
import { InputNumberModule } from 'primeng/inputnumber';
import { AutoCompleteModule, AutoCompleteSelectEvent } from 'primeng/autocomplete';

// Application
import { RealEstateResearchService } from '../../services/real-estate-research.service';
import { RealEstateRequest } from '../../services/real-estate-research-state.service';

interface AddressSuggestion {
  display: string;
  street: string;
  secondary: string;
  city: string;
  state: string;
  zipcode: string;
  entries: number;
}

@Component({
  selector: 'app-real-estate-research-form',
  imports: [InputTextModule, InputNumberModule, AutoCompleteModule, ReactiveFormsModule],
  templateUrl: './real-estate-research-form.component.html',
  styleUrl: './real-estate-research-form.component.css',
})
export class RealEstateResearchFormComponent implements OnInit, OnDestroy {
  private realEstateService = inject(RealEstateResearchService);
  private http = inject(HttpClient);

  submitted = signal(false);
  realEstateForm = new FormGroup<Record<string, FormControl>>({});

  formControls = [
    'streetAddress',
    'city',
    'state',
    'zipCode',
    'purchasePrice', // Optional
    'downPaymentPercent', // Requred
    'loanTermYears', // Required
    'interestRate', // Required (Default to market rate based on down payment percent) - do call in init to grab the rates and update state of global variables
    'estimatedRent', // Optional
    'timeHorizonYears', // Optional
  ];

  addressSuggestions: AddressSuggestion[] = [];

  private searchTerms = new Subject<string>();
  private destroy$ = new Subject<void>();

  ngOnInit() {
    this.makeForm();

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

  makeForm() {
    this.formControls.forEach((control) => {
      this.realEstateForm.addControl(control, new FormControl(null, Validators.required));
    });

    this.realEstateForm.addControl('addressSearch', new FormControl(null));
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
    const raw = this.realEstateForm.getRawValue() as {
      streetAddress?: string | null;
      city?: string | null;
      state?: string | null;
      zipCode?: string | null;
      purchasePrice?: number | null;
      downPaymentPercent?: number | null;
      loanTermYears?: number | null;
      interestRate?: number | null;
      estimatedRent?: number | null;
      timeHorizonYears?: number | null;
    };

    // Build properly formatted address with commas
    const addressParts: string[] = [];

    if (raw.streetAddress?.trim()) {
      addressParts.push(raw.streetAddress.trim());
    }
    if (raw.city?.trim()) {
      addressParts.push(raw.city.trim());
    }
    if (raw.state?.trim()) {
      addressParts.push(raw.state.trim());
    }
    if (raw.zipCode?.trim()) {
      addressParts.push(raw.zipCode.trim());
    }

    const address = addressParts.join(', ');

    // Format field names for Python backend
    const request: RealEstateRequest = {
      address,
      purchase_price: Number(raw.purchasePrice ?? 0),
      down_payment_pct: Number(raw.downPaymentPercent ?? 0),
      loan_term_years: Number(raw.loanTermYears ?? 0),
      interest_rate: Number(raw.interestRate ?? 0),
      estimated_rent: Number(raw.estimatedRent ?? 0),
      time_horizon_years: Number(raw.timeHorizonYears ?? 0),
    };

    this.realEstateService.generateReport(request);
    this.realEstateForm.reset();
  }

  isFieldInvalid(controlName: string): boolean | undefined {
    const control = this.realEstateForm.get(controlName);
    return control?.invalid && (control.touched || this.submitted());
  }
}
