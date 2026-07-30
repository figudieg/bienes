import { Routes } from '@angular/router';
import { Inicio } from './inicio';

export const DASHBOARD_ROUTES: Routes = [
  { path: '', component: Inicio },
  { 
    path: 'sudebin-reportes', 
    loadComponent: () => import('./sudebin-reportes/sudebin-reportes').then(c => c.SudebinReportesComponent) 
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
