// Angular
import { Routes } from '@angular/router';

// Application
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
  { path: '**', redirectTo: '/home' },
];
