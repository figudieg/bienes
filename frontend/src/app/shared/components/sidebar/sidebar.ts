import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { UserRole } from '../../../core/models/user.model';
import { Subscription } from 'rxjs';

interface NavItem {
  label: string;
  icon: string;
  route: string;
  roles: UserRole[];
  sectionLabel?: string;
}

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './sidebar.html',
})
export class SidebarComponent implements OnInit, OnDestroy {
  menuItems: NavItem[] = [
    {
      label: 'Panel Principal',
      icon: 'fas fa-th-large',
      route: '/inicio',
      roles: ['OPERADOR', 'ADMINISTRADOR', 'AUDITOR'],
      sectionLabel: 'INICIO',
    },
    {
      label: 'Registro de Bienes',
      icon: 'fas fa-boxes',
      route: '/bienes',
      roles: ['OPERADOR', 'ADMINISTRADOR', 'AUDITOR'],
      sectionLabel: 'INVENTARIO',
    },
    {
      label: 'Asignaciones',
      icon: 'fas fa-user-tag',
      route: '/asignaciones',
      roles: ['OPERADOR', 'ADMINISTRADOR'],
    },
    {
      label: 'Perfil de Funcionario',
      icon: 'fas fa-address-card',
      route: '/asignaciones/perfil',
      roles: ['OPERADOR', 'ADMINISTRADOR'],
    },
    {
      label: 'Automotores',
      icon: 'fas fa-car',
      route: '/automotor',
      roles: ['OPERADOR', 'ADMINISTRADOR', 'AUDITOR'],
    },
    {
      label: 'Inmuebles',
      icon: 'fas fa-building',
      route: '/inmuebles',
      roles: ['OPERADOR', 'ADMINISTRADOR', 'AUDITOR'],
    },
    {
      label: 'Órdenes de Compra',
      icon: 'fas fa-file-invoice',
      route: '/ordenes',
      roles: ['AUDITOR', 'ADMINISTRADOR'],
      sectionLabel: 'REPORTES',
    },
    {
      label: 'Auditoría e Histórico',
      icon: 'fas fa-history',
      route: '/auditoria',
      roles: ['AUDITOR', 'ADMINISTRADOR'],
    },
    {
      label: 'Reportes de Bienes Públicos',
      icon: 'fas fa-file-excel',
      route: '/inicio/reportes-bienes-publicos',
      roles: ['AUDITOR', 'ADMINISTRADOR'],
    },
    {
      label: 'Buzón de Recuperaciones',
      icon: 'fas fa-envelope-open-text',
      route: '/inicio/bandeja-recuperacion',
      roles: ['ADMINISTRADOR'],
      sectionLabel: 'ADMINISTRACIÓN',
    },
    {
      label: 'Gestión de Usuarios',
      icon: 'fas fa-users-cog',
      route: '/inicio/gestion-usuarios',
      roles: ['ADMINISTRADOR'],
    },
  ];

  filteredMenu: NavItem[] = [];
  vistaCompacta = false;
  private userSub!: Subscription;
  private static readonly STORAGE_KEY = 'phoenixIsNavbarVerticalCollapsed';

  constructor(private authService: AuthService) {}

  ngOnInit(): void {
    this.userSub = this.authService.currentUser$.subscribe(user => {
      if (user) {
        this.filteredMenu = this.menuItems.filter((item) =>
          item.roles.includes(user.rol)
        );
      } else {
        this.filteredMenu = [];
      }
    });

    this.vistaCompacta = localStorage.getItem(SidebarComponent.STORAGE_KEY) === 'true';
    document.documentElement.classList.toggle('navbar-vertical-collapsed', this.vistaCompacta);
  }

  toggleVistaCompacta(): void {
    this.vistaCompacta = !this.vistaCompacta;
    document.documentElement.classList.toggle('navbar-vertical-collapsed', this.vistaCompacta);
    localStorage.setItem(SidebarComponent.STORAGE_KEY, String(this.vistaCompacta));
  }

  ngOnDestroy(): void {
    if (this.userSub) this.userSub.unsubscribe();
  }
}