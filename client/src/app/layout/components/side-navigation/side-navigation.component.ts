import { Component, signal } from '@angular/core';
import { RouterModule } from '@angular/router';

import { DividerModule } from 'primeng/divider';
import { TooltipModule } from 'primeng/tooltip';

import { SideNavItem } from '../../types';

@Component({
  selector: 'app-side-navigation',
  imports: [RouterModule, TooltipModule, DividerModule],
  templateUrl: './side-navigation.component.html',
  styleUrl: './side-navigation.component.css',
})
export class SideNavigationComponent {
  isExpanded = signal(false);

  toggleSidebar() {
    this.isExpanded.update((v) => !v);
  }

  navItems: SideNavItem[] = [
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
  ];
}
