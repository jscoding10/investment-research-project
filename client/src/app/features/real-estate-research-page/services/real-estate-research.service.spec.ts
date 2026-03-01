import { TestBed } from '@angular/core/testing';

import { RealEstateResearchService } from './real-estate-research.service';

describe('RealEstateResearchService', () => {
  let service: RealEstateResearchService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(RealEstateResearchService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
