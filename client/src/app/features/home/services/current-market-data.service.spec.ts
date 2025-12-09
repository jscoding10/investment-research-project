import { TestBed } from '@angular/core/testing';

import { CurrentMarketDataService } from './current-market-data.service';

describe('CurrentMarketDataService', () => {
  let service: CurrentMarketDataService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CurrentMarketDataService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
