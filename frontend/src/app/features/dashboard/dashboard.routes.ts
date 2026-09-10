import { Routes } from '@angular/router';
import { Inicio } from './inicio';

export const DASHBOARD_ROUTES: Routes = [
  { path: '', component: Inicio },
  {
    path: 'reportes-bienes-publicos',
    loadComponent: () => import('./reportes-bienes-publicos/reportes-bienes-publicos').then(c => c.ReportesBienesPublicosComponent)
  },
  {
    path: 'bandeja-recuperacion',
    loadComponent: () => import('./bandeja-recuperacion/bandeja-recuperacion').then(c => c.BandejaRecuperacionComponent)
  },
  {
    path: 'gestion-usuarios',
    loadComponent: () => import('./gestion-usuarios/gestion-usuarios').then(c => c.GestionUsuariosComponent)
  },
];
