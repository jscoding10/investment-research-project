import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CryptoDataTableComponent } from './crypto-data-table.component';

describe('CryptoDataTableComponent', () => {
  let component: CryptoDataTableComponent;
  let fixture: ComponentFixture<CryptoDataTableComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CryptoDataTableComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CryptoDataTableComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
