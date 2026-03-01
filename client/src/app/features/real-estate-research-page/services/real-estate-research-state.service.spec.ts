import { TestBed } from '@angular/core/testing';

import { RealEstateResearchStateService } from './real-estate-research-state.service';

describe('RealEstateResearchStateService', () => {
  let service: RealEstateResearchStateService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(RealEstateResearchStateService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
