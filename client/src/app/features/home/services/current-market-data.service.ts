import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { catchError, Observable, of } from 'rxjs';

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
  private readonly apiUrl = 'http://localhost:8000/stock-table-prices';

  getCurrentStockData(): Observable<StockDataResponse> {
    return this.httpClient.get<StockDataResponse>(`${this.apiUrl}`);
  }
}
// {"data":[{"ticker":"AAPL","name":"AAPL","price":277.96,"change_pct":0.15,"volume":658188,"currency":"USD"},{"ticker":"MSFT","name":"MSFT","price":491.12,"change_pct":0.17,"volume":368344,"currency":"USD"},{"ticker":"GOOGL","name":"GOOGL","price":313.71,"change_pct":0.23,"volume":397084,"currency":"USD"},{"ticker":"AMZN","name":"AMZN","price":226.99,"change_pct":0.14,"volume":661507,"currency":"USD"},{"ticker":"NVDA","name":"NVDA","price":185.58,"change_pct":0.23,"volume":1674649,"currency":"USD"},{"ticker":"META","name":"META","price":667.03,"change_pct":0.03,"volume":211717,"currency":"USD"},{"ticker":"TSLA","name":"TSLA","price":439.59,"change_pct":0.09,"volume":547689,"currency":"USD"}],"failed":[],"updated":"2025-12-09T00:31:15.661502Z","source":"yfinance (bulk + fast_info)"}
