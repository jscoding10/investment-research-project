// Angular
import { Component, output } from '@angular/core';

// PrimeNg
import { ToolbarModule } from 'primeng/toolbar';
import { ButtonModule } from 'primeng/button';

@Component({
  selector: 'app-top-bar',
  imports: [ToolbarModule, ButtonModule],
  templateUrl: './top-bar.component.html',
  styleUrl: './top-bar.component.css',
})
export class TopBarComponent {
  toggleMobileMenu = output<void>();
}
