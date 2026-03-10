import { Component, inject, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';

import { CryptoResearchFormComponent } from '../crypto-research-form/crypto-research-form.component';
import { CryptoResearchReportComponent } from '../crypto-research-report/crypto-research-report.component';

import { CryptoResearchStateService } from '../../services/crypto-research-state.service';

@Component({
  selector: 'app-crypto-research',
  imports: [CommonModule, CryptoResearchFormComponent, CryptoResearchReportComponent],
  templateUrl: './crypto-research.component.html',
  styleUrl: './crypto-research.component.css',
})
export class CryptoResearchComponent implements OnDestroy {
  state = inject(CryptoResearchStateService);
  report = this.state.report;
  isLoading = this.state.isLoading;
  ticker = this.state.ticker;
  error = this.state.error;

  ngOnDestroy() {
    this.state.reset();
  }
}
