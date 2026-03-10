import { StockData } from '.';

export interface StockDataResponse {
  data: StockData[];
  failed: string[];
  updated: string;
  source: string;
}
