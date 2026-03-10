export interface StockRequest {
  ticker: string;
  trade_direction: 'long' | 'short';
  trade_duration: string;
}
