import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CryptoResearchReportComponent } from './crypto-research-report.component';

describe('CryptoResearchReportComponent', () => {
  let component: CryptoResearchReportComponent;
  let fixture: ComponentFixture<CryptoResearchReportComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CryptoResearchReportComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CryptoResearchReportComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
