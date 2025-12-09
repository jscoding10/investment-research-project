import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StockEquityResearchComponent } from './stock-equity-research.component';

describe('StockEquityResearchComponent', () => {
  let component: StockEquityResearchComponent;
  let fixture: ComponentFixture<StockEquityResearchComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [StockEquityResearchComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(StockEquityResearchComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
