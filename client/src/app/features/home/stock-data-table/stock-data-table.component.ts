// Angular
import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CurrencyPipe } from '@angular/common';

// Libraries
import { Subject, takeUntil } from 'rxjs';

import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';
import { CardModule } from 'primeng/card';
import { SkeletonModule } from 'primeng/skeleton';

// Application
import { CurrentMarketDataService, StockData } from '../services/current-market-data.service';

@Component({
  selector: 'app-stock-data-table',
  imports: [CommonModule, TableModule, TagModule, CurrencyPipe, CardModule, SkeletonModule],
  templateUrl: './stock-data-table.component.html',
  styleUrl: './stock-data-table.component.css',
})
export class StockDataTableComponent implements OnInit {
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
}
