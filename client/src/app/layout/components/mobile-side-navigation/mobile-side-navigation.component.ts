import { CommonModule } from '@angular/common';
import { Component, model, signal } from '@angular/core';
import { RouterModule } from '@angular/router';

import { MobileNavItem } from '../../types';

@Component({
  selector: 'app-mobile-side-navigation',
  imports: [CommonModule, RouterModule],
  templateUrl: './mobile-side-navigation.component.html',
  styleUrl: './mobile-side-navigation.component.css',
})
export class MobileSideNavigationComponent {
  // Local nav items — independent from desktop
  navItems = signal<MobileNavItem[]>([
    { label: 'Home', icon: 'home', route: '/home' },
    {
      label: 'Stock Research',
      icon: 'trending_up',
      route: '/stock-equity-research',
    },
    {
      label: 'Crypto Research',
      icon: 'currency_bitcoin',
      route: '/crypto-research',
    },
    {
      label: 'Real Estate',
      icon: 'house',
      route: '/real-estate-research',
    },
  ]);

  // Two-way signal for open state
  open = model.required<boolean>();
}
