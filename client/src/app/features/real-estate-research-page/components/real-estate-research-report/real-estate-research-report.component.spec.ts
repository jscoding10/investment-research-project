import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RealEstateResearchReportComponent } from './real-estate-research-report.component';

describe('RealEstateResearchReportComponent', () => {
  let component: RealEstateResearchReportComponent;
  let fixture: ComponentFixture<RealEstateResearchReportComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RealEstateResearchReportComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RealEstateResearchReportComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
