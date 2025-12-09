import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StockEquityResearchReportComponent } from './stock-equity-research-report.component';

describe('StockEquityResearchReportComponent', () => {
  let component: StockEquityResearchReportComponent;
  let fixture: ComponentFixture<StockEquityResearchReportComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [StockEquityResearchReportComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(StockEquityResearchReportComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
