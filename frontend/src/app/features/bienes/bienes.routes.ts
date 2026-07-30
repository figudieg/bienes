import { Routes } from '@angular/router';

export const BIENES_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('./pages/lista-bienes/lista-bienes').then(m => m.ListaBienesComponent)
  },
  {
    path: 'nuevo',
    loadComponent: () => import('./pages/registro-bien/registro-bien').then(m => m.RegistroBienComponent)
  },
  {
    path: 'editar/:id',
    loadComponent: () => import('./pages/registro-bien/registro-bien').then(m => m.RegistroBienComponent)
  }
];
