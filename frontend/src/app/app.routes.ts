import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth-guard';
import { roleGuard } from './core/guards/role.guard';

export const routes: Routes = [
  // Ruta inicial: Login
  { 
    path: '', 
    loadChildren: () => import('./features/auth/auth.routes').then(m => m.AUTH_ROUTES) 
  },
  
  // Dashboard / Inicio
  { 
    path: 'inicio', 
    loadChildren: () => import('./features/dashboard/dashboard.routes').then(m => m.DASHBOARD_ROUTES),
    canActivate: [authGuard]
  },

  // Módulo de Bienes Públicos (todos los roles autenticados)
  {
    path: 'bienes',
    loadChildren: () => import('./features/bienes/bienes.routes').then(m => m.BIENES_ROUTES),
    canActivate: [authGuard]
  },

  // Módulo de Asignaciones (OPERADOR y ADMINISTRADOR)
  {
    path: 'asignaciones',
    loadChildren: () => import('./features/asignaciones/asignaciones.routes').then(m => m.ASIGNACIONES_ROUTES),
    canActivate: [authGuard, roleGuard],
    data: { roles: ['OPERADOR', 'ADMINISTRADOR'] }
  },

  // Módulo de Órdenes de Compra y Reportes PDF
  {
    path: 'ordenes',
    loadChildren: () => import('./features/ordenes/ordenes.routes').then(m => m.ORDENES_ROUTES),
    canActivate: [authGuard, roleGuard],
    data: { roles: ['AUDITOR', 'ADMINISTRADOR'] }
  },

  // Módulo de Auditoría / Histórico (AUDITOR y ADMINISTRADOR)
  {
    path: 'auditoria',
    loadChildren: () => import('./features/auditoria/auditoria.routes').then(m => m.AUDITORIA_ROUTES),
    canActivate: [authGuard, roleGuard],
    data: { roles: ['AUDITOR', 'ADMINISTRADOR'] }
  },

  // Módulo de Automotores
  {
    path: 'automotor',
    loadChildren: () => import('./features/automotor/automotor.routes').then(m => m.AUTOMOTOR_ROUTES),
    canActivate: [authGuard]
  },

  // Módulo de Inmuebles
  {
    path: 'inmuebles',
    loadChildren: () => import('./features/inmuebles/inmuebles.routes').then(m => m.INMUEBLES_ROUTES),
    canActivate: [authGuard]
  },

  // Manejo de errores 404
  { path: '**', redirectTo: '' }
];