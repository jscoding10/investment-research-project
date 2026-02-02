// Angular
import { Component, inject, OnDestroy, OnInit, signal } from '@angular/core';
import { FormControl, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';

// Libraries
import { CardModule } from 'primeng/card';
import { DrawerModule } from 'primeng/drawer';
import { ButtonModule } from 'primeng/button';
import { SelectModule } from 'primeng/select';
import { MessageModule } from 'primeng/message';
import { InputTextModule } from 'primeng/inputtext';

import { Subject, takeUntil } from 'rxjs';

// Application
import { MarketDataComponent } from '../market-data/market-data.component';

interface InvestmentTypeOption {
  name: string;
  code: string;
}

@Component({
  selector: 'app-home-page',
  imports: [
    MarketDataComponent,
    CardModule,
    DrawerModule,
    ButtonModule,
    SelectModule,
    FormsModule,
    ReactiveFormsModule,
    MessageModule,
    InputTextModule,
  ],
  templateUrl: './home-page.component.html',
  styleUrl: './home-page.component.css',
})
export class HomePageComponent implements OnInit, OnDestroy {
  // Used for PrimeNg Select Options
  investmentTypes: Array<InvestmentTypeOption> = [
    { name: 'Stocks', code: 'stock' },
    { name: 'Crypto', code: 'crypto' },
    { name: 'Single-Family Home', code: 'home' },
  ];

  // Array of form control names
  formControls = ['investmentType'];

  // Signal to determine whether form is submitted or not
  submitted = signal(false);

  // Emits a signal when the component is being destroyed.
  // Used with takeUntil() to automatically unsubscribe from all Observables.
  private destroy$ = new Subject<void>();

  // Initialize form group to empty object
  homepageForm = new FormGroup({});

  router = inject(Router);

  ngOnInit() {
    // Populate form group
    this.makeForm();

    // Subscribe to form value changes and auto-unsubscribe when destroy$ emits.
    // Prevents memory leaks from long-lived subscriptions.
    this.homepageForm.valueChanges.pipe(takeUntil(this.destroy$)).subscribe(() => {
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
      this.homepageForm.addControl(control, new FormControl('', Validators.required));
    });
  }

  onSubmit(): void {
    this.submitted.set(true);

    if (this.homepageForm.invalid) {
      this.homepageForm.markAllAsTouched();
      return;
    }

    if (this.homepageForm.get('investmentType')?.value === 'stock') {
      this.router.navigate(['stock-equity-research']);
    }

    if (this.homepageForm.get('investmentType')?.value === 'crypto') {
      this.router.navigate(['crypto-research']);
    }

    if (this.homepageForm.get('investmentType')?.value === 'home') {
      this.router.navigate(['investment-property']);
    }
  }

  // Method to determine if form control is invalid
  isFieldInvalid(controlName: string): boolean | undefined {
    const control = this.homepageForm.get(controlName);
    return control?.invalid && (control.touched || this.submitted());
  }

  get investmentType() {
    return this.homepageForm.get('investmentType');
  }

  get investmentDescription() {
    return this.homepageForm.get('investmentDescription');
  }
}
