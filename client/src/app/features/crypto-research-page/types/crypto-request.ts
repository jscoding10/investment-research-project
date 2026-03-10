export interface CryptoRequest {
  ticker: string;
  trade_direction: 'long' | 'short';
  trade_duration: string;
}
