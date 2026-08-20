import { Routes } from '@angular/router';

export const ASIGNACIONES_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('./pages/lista-asignaciones/lista-asignaciones').then(m => m.ListaAsignacionesComponent)
  },
  {
    path: 'nueva',
    loadComponent: () => import('./pages/nueva-asignacion/nueva-asignacion').then(m => m.NuevaAsignacionComponent)
  },
  {
    path: 'perfil',
    loadComponent: () => import('./pages/perfil-funcionario/perfil-funcionario').then(m => m.PerfilFuncionarioComponent)
  }
];
