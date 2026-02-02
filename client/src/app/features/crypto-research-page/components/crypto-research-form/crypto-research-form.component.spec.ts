import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CryptoResearchFormComponent } from './crypto-research-form.component';

describe('CryptoResearchFormComponent', () => {
  let component: CryptoResearchFormComponent;
  let fixture: ComponentFixture<CryptoResearchFormComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CryptoResearchFormComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CryptoResearchFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
