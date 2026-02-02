import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CryptoResearchComponent } from './crypto-research.component';

describe('CryptoResearchComponent', () => {
  let component: CryptoResearchComponent;
  let fixture: ComponentFixture<CryptoResearchComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CryptoResearchComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CryptoResearchComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
