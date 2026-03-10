import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { SelectButtonModule } from 'primeng/selectbutton';

import { CryptoDataTableComponent } from '../crypto-data-table/crypto-data-table.component';
import { StockDataTableComponent } from '../stock-data-table/stock-data-table.component';

@Component({
  selector: 'app-market-data',
  imports: [SelectButtonModule, FormsModule, StockDataTableComponent, CryptoDataTableComponent],
  templateUrl: './market-data.component.html',
  styleUrl: './market-data.component.css',
})
export class MarketDataComponent {
  selectedInvestment: 'stocks' | 'crypto' = 'stocks';

  investmentTypes = [
    { label: 'Stocks', value: 'stocks' },
    { label: 'Crypto', value: 'crypto' },
  ];
}
