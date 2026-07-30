import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';
import Swal from 'sweetalert2';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('currentUser');
        router.navigate(['/']);
        if (!req.url.includes('/auth/login/')) {
          Swal.fire('Sesión Expirada', 'Por favor, inicie sesión nuevamente.', 'warning');
        }
      } else if (error.status === 0) {
        Swal.fire('Error de Conexión', 'No se pudo conectar con el servidor.', 'error');
      }
      return throwError(() => error);
    })
  );
};
