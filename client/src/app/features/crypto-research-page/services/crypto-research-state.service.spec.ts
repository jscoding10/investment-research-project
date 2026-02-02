import { TestBed } from '@angular/core/testing';

import { CryptoResearchStateService } from './crypto-research-state.service';

describe('CryptoResearchStateService', () => {
  let service: CryptoResearchStateService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CryptoResearchStateService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
