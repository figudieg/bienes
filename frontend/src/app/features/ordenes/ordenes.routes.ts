import { Routes } from '@angular/router';

export const ORDENES_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('./pages/lista-ordenes/lista-ordenes').then(m => m.ListaOrdenesComponent)
  }
];
