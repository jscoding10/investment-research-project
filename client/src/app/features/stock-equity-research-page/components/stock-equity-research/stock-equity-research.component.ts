import { CommonModule } from '@angular/common';
import { Component, inject, OnDestroy } from '@angular/core';

import { StockEquityResearchFormComponent } from '../stock-equity-research-form/stock-equity-research-form.component';
import { StockEquityResearchReportComponent } from '../stock-equity-research-report/stock-equity-research-report.component';

import { StockEquityResearchStateService } from '../../services/stock-equity-research-state.service';

@Component({
  selector: 'app-stock-equity-research',
  imports: [CommonModule, StockEquityResearchFormComponent, StockEquityResearchReportComponent],
  templateUrl: './stock-equity-research.component.html',
  styleUrl: './stock-equity-research.component.css',
})
export class StockEquityResearchComponent implements OnDestroy {
  state = inject(StockEquityResearchStateService);
  report = this.state.report;
  isLoading = this.state.isLoading;
  ticker = this.state.ticker;
  error = this.state.error;

  ngOnDestroy() {
    this.state.reset();
  }
}
