import { Router } from '@angular/router';
import Swal from 'sweetalert2';

// Evita mostrar la alerta más de una vez si varias peticiones en paralelo
// detectan la expiración al mismo tiempo (ej. una pantalla que carga 3-4
// listas juntas al entrar).
let mostrandoAlerta = false;

/** Limpia la sesión local y avisa al usuario, solo si de verdad tenía una sesión abierta. */
export function cerrarSesionPorExpiracion(router: Router) {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('currentUser');

  if (mostrandoAlerta) return;
  mostrandoAlerta = true;

  router.navigate(['/']);
  Swal.fire('Sesión Expirada', 'Por favor, inicie sesión nuevamente.', 'warning').then(() => {
    mostrandoAlerta = false;
  });
}
