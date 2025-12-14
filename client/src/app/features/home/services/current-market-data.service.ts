import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { catchError, Observable, of } from 'rxjs';
import { environment } from '../../../../../environments/environment';

export interface StockData {
  ticker: string;
  name: string;
  price: number;
  change_pct: number;
  volume: number;
  currency: string;
}

interface StockDataResponse {
  data: StockData[];
  failed: string[];
  updated: string;
  source: string;
}

@Injectable({
  providedIn: 'root',
})
export class CurrentMarketDataService {
  httpClient = inject(HttpClient);
  private readonly baseUrl = environment.apiBaseUrl;

  getCurrentStockData(): Observable<StockDataResponse> {
    return this.httpClient.get<StockDataResponse>(`${this.baseUrl}/stock-table-prices`);
  }
}
