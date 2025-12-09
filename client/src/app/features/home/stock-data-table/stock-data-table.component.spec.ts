import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StockDataTableComponent } from './stock-data-table.component';

describe('StockDataTableComponent', () => {
  let component: StockDataTableComponent;
  let fixture: ComponentFixture<StockDataTableComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [StockDataTableComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(StockDataTableComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
