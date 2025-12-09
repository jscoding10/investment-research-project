import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StockEquityResearchFormComponent } from './stock-equity-research-form.component';

describe('StockEquityResearchFormComponent', () => {
  let component: StockEquityResearchFormComponent;
  let fixture: ComponentFixture<StockEquityResearchFormComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [StockEquityResearchFormComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(StockEquityResearchFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
