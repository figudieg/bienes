import { ErrorHandler, Injectable, NgZone } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import Swal from 'sweetalert2';

/**
 * Cualquier excepción de JavaScript no controlada (un bug de plantilla, un
 * null inesperado, etc.) cae aquí en vez de dejar la pantalla congelada sin
 * explicación. Nunca mostramos el mensaje técnico — solo pedimos recargar.
 * Los errores HTTP los maneja `error-interceptor.ts`; este handler los ignora
 * para no duplicar la alerta.
 */
@Injectable()
export class GlobalErrorHandler implements ErrorHandler {
  private ultimaAlerta = 0;

  constructor(private zone: NgZone) {}

  handleError(error: unknown): void {
    console.error('Error no controlado:', error);

    if (error instanceof HttpErrorResponse) return;

    const ahora = Date.now();
    if (ahora - this.ultimaAlerta < 4000) return; // evita alertas repetidas en cascada
    this.ultimaAlerta = ahora;

    this.zone.run(() => {
      Swal.fire(
        'Algo salió mal',
        'Ocurrió un problema inesperado en la página. Por favor, recárguela e intente nuevamente.',
        'error'
      );
    });
  }
}
