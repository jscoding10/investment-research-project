import { CryptoData } from './crypto-data';

export interface CryptoDataResponse {
  data: CryptoData[];
  failed: string[];
  updated: string;
  source: string;
}
