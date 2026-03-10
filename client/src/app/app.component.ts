import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';

import { FooterComponent } from './layout/components/footer/footer.component';
import { MobileSideNavigationComponent } from './layout/components/mobile-side-navigation/mobile-side-navigation.component';
import { SideNavigationComponent } from './layout/components/side-navigation/side-navigation.component';
import { TopBarComponent } from './layout/components/top-bar/top-bar.component';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, TopBarComponent, SideNavigationComponent, FooterComponent, MobileSideNavigationComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent {
  title = 'client';
  isMobileMenuOpen = signal(false);

  toggleMobileMenu() {
    this.isMobileMenuOpen.update((v) => !v);
  }

  closeMobileMenu() {
    this.isMobileMenuOpen.set(false);
  }
}
