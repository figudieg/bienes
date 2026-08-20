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
      label: 'Reportes SUDEBIN',
      icon: 'fas fa-file-excel',
      route: '/inicio/sudebin-reportes',
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
  private userSub!: Subscription;

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
  }

  ngOnDestroy(): void {
    if (this.userSub) this.userSub.unsubscribe();
  }
}