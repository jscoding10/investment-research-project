// Angular
import { Component, inject, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';

// Application
import { RealEstateResearchFormComponent } from '../real-estate-research-form/real-estate-research-form.component';
import { RealEstateResearchReportComponent } from '../real-estate-research-report/real-estate-research-report.component';
import { RealEstateResearchStateService } from '../../services/real-estate-research-state.service';

@Component({
  selector: 'app-real-estate-research',
  imports: [CommonModule, RealEstateResearchFormComponent, RealEstateResearchReportComponent],
  templateUrl: './real-estate-research.component.html',
  styleUrl: './real-estate-research.component.css',
})
export class RealEstateResearchComponent implements OnDestroy {
  state = inject(RealEstateResearchStateService);

  report = this.state.report;
  isLoading = this.state.isLoading;
  address = this.state.address;
  error = this.state.error;

  ngOnDestroy() {
    this.state.reset();
  }
}
