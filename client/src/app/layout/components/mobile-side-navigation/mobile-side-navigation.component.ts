// Angular
import { Component, model, signal } from '@angular/core';
import { RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';

interface NavItem {
  label: string;
  icon: string;
  route: string;
}

@Component({
  selector: 'app-mobile-side-navigation',
  imports: [CommonModule, RouterModule],
  templateUrl: './mobile-side-navigation.component.html',
  styleUrl: './mobile-side-navigation.component.css',
})
export class MobileSideNavigationComponent {
  // Local nav items — independent from desktop
  navItems = signal<NavItem[]>([
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
      label: 'Investment Property',
      icon: 'apartment',
      route: '/investment-property',
    },
  ]);

  // Two-way signal for open state
  open = model.required<boolean>();
}
