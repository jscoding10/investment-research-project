import { TestBed } from '@angular/core/testing';

import { StockResearchService } from './stock-research.service';

describe('StockResearchService', () => {
  let service: StockResearchService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(StockResearchService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
