import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { UserRole } from '../models/user.model';

export const roleGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  // Primero verificar si está logueado
  if (!authService.isAuthenticated()) {
    router.navigate(['/']);
    return false;
  }

  // Verificar si la ruta requiere roles específicos
  const expectedRoles = route.data['roles'] as Array<UserRole>;
  const currentUser = authService.getCurrentUser();

  if (expectedRoles && currentUser) {
    if (!expectedRoles.includes(currentUser.rol)) {
      // Si el rol no está permitido, redirigir al dashboard base o mostrar error
      router.navigate(['/inicio']);
      return false;
    }
  }

  return true;
};
