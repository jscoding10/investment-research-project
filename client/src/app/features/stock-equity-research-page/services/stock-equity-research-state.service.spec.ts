import { TestBed } from '@angular/core/testing';

import { StockEquityResearchStateService } from './stock-equity-research-state.service';

describe('StockEquityResearchStateService', () => {
  let service: StockEquityResearchStateService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(StockEquityResearchStateService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
