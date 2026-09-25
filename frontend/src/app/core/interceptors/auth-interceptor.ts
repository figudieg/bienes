import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { isTokenExpired } from '../utils/jwt.util';
import { cerrarSesionPorExpiracion } from '../utils/sesion-expirada.util';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = localStorage.getItem('access_token');

  if (token && !isTokenExpired(token)) {
    const authReq = req.clone({
      headers: req.headers.set('Authorization', `Bearer ${token}`)
    });
    return next(authReq);
  }

  if (token) {
    // Token vencido localmente: se trata igual que si el servidor hubiera
    // respondido 401, para no dejar la pantalla cargando en silencio con un
    // error genérico de "no se pudo cargar" cuando en realidad es la sesión.
    cerrarSesionPorExpiracion(inject(Router));
  }

  return next(req);
};
