// Angular
import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';

// PrimeNg
import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';
import { CurrencyPipe } from '@angular/common';
import { CardModule } from 'primeng/card';
import { SkeletonModule } from 'primeng/skeleton';
import { CurrentMarketDataService, StockData } from '../services/current-market-data.service';
import { Subject, takeUntil } from 'rxjs';

// interface Stock {
//   ticker: string;
//   name: string;
//   price: number;
//   change_pct: number;
//   volume: string;
//   currency: string;
// }

@Component({
  selector: 'app-stock-data-table',
  imports: [CommonModule, TableModule, TagModule, CurrencyPipe, CardModule, SkeletonModule],
  templateUrl: './stock-data-table.component.html',
  styleUrl: './stock-data-table.component.css',
})
export class StockDataTableComponent {
  stocks: StockData[] = [];
  isLoading = true;

  private destroy$ = new Subject<void>();

  currentMarketDataService = inject(CurrentMarketDataService);
  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.isLoading = true;
    this.currentMarketDataService
      .getCurrentStockData()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (res) => {
          this.stocks = res.data ?? [];
          this.isLoading = false;
        },
        error: () => {
          this.stocks = [];
          this.isLoading = false;
        },
      });
  }

  // New: format volume only for display
  formatVolume(volume: number): string {
    if (volume >= 1_000_000) {
      return (volume / 1_000_000).toFixed(2).replace(/\.00$/, '') + 'M';
    }
    if (volume >= 1_000) {
      return (volume / 1_000).toFixed(1).replace(/\.0$/, '') + 'K';
    }
    return volume.toString();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
  // stocks: Stock[] = [
  //   {
  //     ticker: 'AAPL',
  //     name: 'Apple Inc.',
  //     price: 182.52,
  //     change_pct: 1.24,
  //     volume: '52.3M',
  //     currency: 'USD',
  //   },
  //   {
  //     ticker: 'GOOGL',
  //     name: 'Alphabet Inc.',
  //     price: 2781.35,
  //     change_pct: -0.82,
  //     volume: '28.1M',
  //     currency: 'USD',
  //   },
  //   {
  //     ticker: 'TSLA',
  //     name: 'Tesla, Inc.',
  //     price: 1012.06,
  //     change_pct: 3.15,
  //     volume: '87.4M',
  //     currency: 'USD',
  //   },
  //   {
  //     ticker: 'MSFT',
  //     name: 'Microsoft Corp.',
  //     price: 415.28,
  //     change_pct: 0.45,
  //     volume: '31.9M',
  //     currency: 'USD',
  //   },
  //   {
  //     ticker: 'NVDA',
  //     name: 'NVIDIA Corporation',
  //     price: 875.42,
  //     change_pct: -2.31,
  //     volume: '44.7M',
  //     currency: 'USD',
  //   },
  // ];
}
