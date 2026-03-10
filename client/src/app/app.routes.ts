import { Routes } from '@angular/router';

import { HomePageComponent } from './features/home/home-page/home-page.component';

export const routes: Routes = [
  { path: '', redirectTo: '/home', pathMatch: 'full' },
  { path: 'home', component: HomePageComponent },
  {
    path: 'stock-equity-research',
    loadComponent: () =>
      import('./features/stock-equity-research-page/components/stock-equity-research/stock-equity-research.component').then(
        (m) => m.StockEquityResearchComponent,
      ),
  },
  {
    path: 'crypto-research',
    loadComponent: () =>
      import('./features/crypto-research-page/components/crypto-research/crypto-research.component').then(
        (m) => m.CryptoResearchComponent,
      ),
  },
  {
    path: 'real-estate-research',
    loadComponent: () =>
      import('./features/real-estate-research-page/components/real-estate-research/real-estate-research.component').then(
        (m) => m.RealEstateResearchComponent,
      ),
  },

  { path: '**', redirectTo: '/home' },
];
