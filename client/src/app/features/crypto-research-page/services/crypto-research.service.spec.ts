import { TestBed } from '@angular/core/testing';

import { CryptoResearchService } from './crypto-research.service';

describe('CryptoResearchService', () => {
  let service: CryptoResearchService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CryptoResearchService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
