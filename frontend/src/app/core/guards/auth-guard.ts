import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { isTokenExpired } from '../utils/jwt.util';
import { cerrarSesionPorExpiracion } from '../utils/sesion-expirada.util';

export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);
  const token = localStorage.getItem('access_token');

  if (!authService.isAuthenticated()) {
    router.navigate(['/']);
    return false;
  }

  if (isTokenExpired(token)) {
    // Había un token guardado pero ya venció: se avisa, a diferencia de un
    // visitante que nunca inició sesión (ese caso no debe ver esta alerta).
    cerrarSesionPorExpiracion(router);
    return false;
  }

  return true;
};
