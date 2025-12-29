// Angular
import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';

// PrimeNg
import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';
import { CurrencyPipe } from '@angular/common';
import { CardModule } from 'primeng/card';
import { SkeletonModule } from 'primeng/skeleton';
import { CryptoData, CurrentMarketDataService } from '../services/current-market-data.service';
import { Subject, takeUntil } from 'rxjs';

@Component({
  selector: 'app-crypto-data-table',
  imports: [CommonModule, TableModule, TagModule, CurrencyPipe, CardModule, SkeletonModule],
  templateUrl: './crypto-data-table.component.html',
  styleUrl: './crypto-data-table.component.css',
})
export class CryptoDataTableComponent implements OnInit {
  crypto: CryptoData[] = [];
  isLoading = true;

  private destroy$ = new Subject<void>();

  currentMarketDataService = inject(CurrentMarketDataService);
  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.isLoading = true;
    this.currentMarketDataService
      .getCurrentCryptoData()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (res) => {
          this.crypto = (res.data ?? []).map((item) => ({
            ...item,
            displayName: item.name.replace(/\s*USD$/i, '').trim(), // Removes " USD" or " usd" at the end
          }));
          this.isLoading = false;
        },
        error: () => {
          this.crypto = [];
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
