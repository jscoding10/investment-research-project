// Angular
import { Routes } from '@angular/router';

// Application
import { HomePageComponent } from './features/home/home-page/home-page.component';
import { StockEquityResearchComponent } from './features/stock-equity-research-page/components/stock-equity-research/stock-equity-research.component';
// import { CryptoComponent } from './features/crypto/crypto.component';
// import { PropertyComponent } from './features/property/property.component';

// import { StocksRe
// import { CryptoResearchComponent } from './crypto-research/crypto-research.component';
// import { PropertyResearchComponent } from './property-research/property-research.component';

// export const routes: Routes = [
//   {
//     path: '',
//     loadComponent: () =>
//       import('./features/home/home.component').then((m) => m.HomeComponent),
//   },
//   {
//     path: 'stocks',
//     loadComponent: () =>
//       import('./features/stocks/stocks.component').then(
//         (m) => m.StocksComponent
//       ),
//   },
//   {
//     path: 'crypto',
//     loadComponent: () =>
//       import('./features/crypto/crypto.component').then(
//         (m) => m.CryptoComponent
//       ),
//   },
//   {
//     path: 'property',
//     loadComponent: () =>
//       import('./features/property/property.component').then(
//         (m) => m.PropertyComponent
//       ),
//   },
//   { path: '**', redirectTo: '' },
// ];

export const routes: Routes = [
  { path: '', redirectTo: '/home', pathMatch: 'full' },
  { path: 'home', component: HomePageComponent },
  //   { path: 'stock-equity-research', component: StockEquityResearchComponent },
  {
    path: 'stock-equity-research',
    loadComponent: () =>
      import('./features/stock-equity-research-page/components/stock-equity-research/stock-equity-research.component').then(
        (m) => m.StockEquityResearchComponent,
      ),
  },
  //   {
  //     path: 'crypto',
  //     loadComponent: () =>
  //       import('./features/crypto/crypto.component').then(
  //         (m) => m.CryptoComponent
  //       ),
  //   },
  //   { path: 'crypto-equity-research', component: CryptoComponent },
  //   { path: 'investment-property', component: PropertyComponent },
  { path: '**', redirectTo: '/home' },
];
