import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, NavigationEnd, Router } from '@angular/router';
import { filter } from 'rxjs/operators';

// Importamos los nuevos componentes modulares
import { SidebarComponent } from './shared/components/sidebar/sidebar';
import { NavbarComponent } from './shared/components/navbar/navbar';
import { FooterComponent } from './shared/components/footer/footer';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, SidebarComponent, NavbarComponent, FooterComponent],
  templateUrl: './app.html',
  styleUrls: ['./app.css'],
})
export class App implements OnInit {
  showNavbar: boolean = false;
  private publicRoutes = ['', '/', '/login'];

  constructor(private router: Router) {}

  ngOnInit() {
    this.router.events
      .pipe(filter((event) => event instanceof NavigationEnd))
      .subscribe((event: any) => {
        const cleanUrl = event.urlAfterRedirects.split('?')[0];
        // Si la ruta es el login (raíz), ocultamos el menú
        this.showNavbar = !this.publicRoutes.includes(cleanUrl);
      });
  }

  handleSidebarToggle() {
    document.documentElement.classList.toggle('navbar-vertical-collapsed');
  }
}
