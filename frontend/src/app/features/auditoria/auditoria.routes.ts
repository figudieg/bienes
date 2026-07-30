import { Routes } from '@angular/router';

export const AUDITORIA_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('./pages/lista-logs/lista-logs').then(m => m.ListaLogsComponent)
  }
];
