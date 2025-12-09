import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MobileSideNavigationComponent } from './mobile-side-navigation.component';

describe('MobileSideNavigationComponent', () => {
  let component: MobileSideNavigationComponent;
  let fixture: ComponentFixture<MobileSideNavigationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MobileSideNavigationComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MobileSideNavigationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
