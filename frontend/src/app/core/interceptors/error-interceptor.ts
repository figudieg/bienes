import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';
import Swal from 'sweetalert2';
import { cerrarSesionPorExpiracion } from '../utils/sesion-expirada.util';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401) {
        // Solo avisamos y redirigimos si el usuario de verdad creía tener
        // una sesión abierta. Si no había token, este 401 es de una petición
        // de fondo hecha sin login (ej. el chequeo de estado al cargar la
        // página) y no debe interrumpir a alguien que ni siquiera ha entrado.
        const teniaSesion = !!localStorage.getItem('access_token');
        if (teniaSesion && !req.url.includes('/auth/login/')) {
          cerrarSesionPorExpiracion(router);
        } else {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('currentUser');
        }
      } else if (error.status === 0) {
        Swal.fire('Sin conexión', 'No se pudo conectar con el servidor. Verifique su conexión a internet e intente nuevamente.', 'warning');
      } else if (error.status >= 500) {
        // Nunca mostramos el detalle técnico del error del servidor (traceback, HTML de Django, etc.):
        // solo pedimos reintentar o recargar, igual para cualquier módulo del sistema.
        Swal.fire('Algo salió mal', 'Ocurrió un problema inesperado en el sistema. Intente nuevamente en unos minutos; si el problema persiste, recargue la página.', 'error');
      }
      return throwError(() => error);
    })
  );
};
