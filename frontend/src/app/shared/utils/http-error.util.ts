import Swal from 'sweetalert2';

/**
 * Interpreta un error HTTP y devuelve un mensaje apto para el usuario final.
 * Nunca expone detalles técnicos (tracebacks, HTML de Django, etc.) — solo
 * distingue entre "sin conexión", "problema del servidor" y "datos inválidos".
 */
export function mensajeErrorHttp(
  err: any,
  opciones?: { mensajeValidacion?: () => string | undefined | null; mensajeFallback?: string }
): { titulo: string; texto: string; icono: 'error' | 'warning' } {

  if (!err || err.status === 0) {
    return {
      titulo: 'Sin conexión',
      texto: 'No se pudo conectar con el servidor. Verifique su conexión a internet e intente nuevamente.',
      icono: 'warning'
    };
  }

  if (err.status >= 500) {
    return {
      titulo: 'Algo salió mal',
      texto: 'Ocurrió un problema inesperado en el sistema. Intente nuevamente en unos minutos; si el problema persiste, recargue la página.',
      icono: 'error'
    };
  }

  if (err.status === 403) {
    return {
      titulo: 'Sin permiso',
      texto: 'No tiene permisos para realizar esta acción. Si cree que es un error, contacte al administrador.',
      icono: 'warning'
    };
  }

  if (err.status === 404) {
    return {
      titulo: 'No encontrado',
      texto: 'El registro solicitado no existe o ya fue eliminado.',
      icono: 'warning'
    };
  }

  const mensajeCampo = opciones?.mensajeValidacion?.();
  return {
    titulo: 'Revise los datos',
    texto: mensajeCampo || opciones?.mensajeFallback || 'No se pudo completar la operación. Verifique los datos ingresados.',
    icono: 'warning'
  };
}

/**
 * Atajo: interpreta el error y lo muestra con SweetAlert2.
 * Si es un fallo de conexión (status 0) o un error del servidor (5xx), NO
 * muestra nada aquí — el interceptor global (`error-interceptor.ts`) ya le
 * avisó al usuario una sola vez; esta función solo cubre los casos
 * específicos de cada acción (datos inválidos, sin permiso, no encontrado).
 */
export function mostrarErrorHttp(
  err: any,
  opciones?: { mensajeValidacion?: () => string | undefined | null; mensajeFallback?: string }
) {
  if (!err || err.status === 0 || err.status >= 500) return;
  const { titulo, texto, icono } = mensajeErrorHttp(err, opciones);
  Swal.fire(titulo, texto, icono);
}
