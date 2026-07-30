import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, NavigationEnd, Router } from '@angular/router';
import { filter } from 'rxjs/operators';

// Importamos los nuevos componentes modulares
import { SidebarComponent } from './shared/components/sidebar/sidebar';
import { NavbarComponent } from './shared/components/navbar/navbar';
import { FooterComponent } from './shared/components/footer/footer';
import { InventarioService } from './core/services/inventario.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, SidebarComponent, NavbarComponent, FooterComponent],
  templateUrl: './app.html',
  styleUrls: ['./app.css'],
})
export class App implements OnInit {
  showNavbar: boolean = false;
  isSqliteFallback: boolean = false;
  private publicRoutes = ['', '/', '/login'];

  constructor(
    private router: Router,
    private inventarioService: InventarioService
  ) {}

  ngOnInit() {
    this.checkDbStatus();
    this.router.events
      .pipe(filter((event) => event instanceof NavigationEnd))
      .subscribe((event: any) => {
        const cleanUrl = event.urlAfterRedirects.split('?')[0];
        // Si la ruta es el login (raíz), ocultamos el menú
        this.showNavbar = !this.publicRoutes.includes(cleanUrl);
      });
  }

  checkDbStatus() {
    this.inventarioService.getDbStatus().subscribe({
      next: (res) => {
        this.isSqliteFallback = res.engine === 'sqlite';
      },
      error: (err) => {
        console.error('Error al consultar estado de la base de datos:', err);
      }
    });
  }

  handleSidebarToggle() {
    document.documentElement.classList.toggle('navbar-vertical-collapsed');
  }
}
