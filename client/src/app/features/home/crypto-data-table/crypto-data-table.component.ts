// Angular
import { Component } from '@angular/core';
import { CommonModule, CurrencyPipe } from '@angular/common';

// PrimeNg
import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';

interface Crypto {
  ticker: string;
  name: string;
  price: number;
  change_pct: number;
  volume: string;
  currency: string;
}

@Component({
  selector: 'app-crypto-data-table',
  imports: [CommonModule, TableModule, TagModule, CurrencyPipe],
  templateUrl: './crypto-data-table.component.html',
  styleUrl: './crypto-data-table.component.css',
})
export class CryptoDataTableComponent {
  cryptos: Crypto[] = [
    {
      ticker: 'BTC',
      name: 'Bitcoin',
      price: 68234.51,
      change_pct: 2.81,
      volume: '$38.2B',
      currency: 'USD',
    },
    {
      ticker: 'ETH',
      name: 'Ethereum',
      price: 3456.19,
      change_pct: -1.23,
      volume: '$18.9B',
      currency: 'USD',
    },
    {
      ticker: 'SOL',
      name: 'Solana',
      price: 148.77,
      change_pct: 5.67,
      volume: '$4.1B',
      currency: 'USD',
    },
    {
      ticker: 'ADA',
      name: 'Cardano',
      price: 0.587,
      change_pct: -0.45,
      volume: '$892M',
      currency: 'USD',
    },
    {
      ticker: 'XRP',
      name: 'Ripple',
      price: 0.6241,
      change_pct: 1.92,
      volume: '$2.3B',
      currency: 'USD',
    },
  ];
}
