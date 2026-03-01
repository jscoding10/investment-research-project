import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RealEstateResearchFormComponent } from './real-estate-research-form.component';

describe('RealEstateResearchFormComponent', () => {
  let component: RealEstateResearchFormComponent;
  let fixture: ComponentFixture<RealEstateResearchFormComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RealEstateResearchFormComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RealEstateResearchFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
