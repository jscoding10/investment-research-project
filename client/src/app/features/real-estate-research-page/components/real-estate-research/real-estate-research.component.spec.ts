import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RealEstateResearchComponent } from './real-estate-research.component';

describe('RealEstateResearchComponent', () => {
  let component: RealEstateResearchComponent;
  let fixture: ComponentFixture<RealEstateResearchComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RealEstateResearchComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RealEstateResearchComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
