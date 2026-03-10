import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';

import { Observable } from 'rxjs';

import { CryptoDataResponse, StockDataResponse } from '../types';

import { environment } from '../../../../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class CurrentMarketDataService {
  httpClient = inject(HttpClient);
  private readonly baseUrl = environment.apiBaseUrl;

  getCurrentStockData(): Observable<StockDataResponse> {
    return this.httpClient.get<StockDataResponse>(`${this.baseUrl}/stock-table-prices`);
  }

  getCurrentCryptoData(): Observable<CryptoDataResponse> {
    return this.httpClient.get<CryptoDataResponse>(`${this.baseUrl}/crypto-table-prices`);
  }
}
