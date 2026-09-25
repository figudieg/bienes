/** Decodifica el payload de un JWT y revisa si ya venció (claim "exp", en segundos).
 * Si el token no se puede leer, se trata como vencido. */
export function isTokenExpired(token: string | null | undefined): boolean {
  if (!token) return true;
  try {
    const payload = token.split('.')[1];
    const decoded = JSON.parse(atob(payload.replace(/-/g, '+').replace(/_/g, '/')));
    if (!decoded.exp) return false;
    return Date.now() >= decoded.exp * 1000;
  } catch {
    return true;
  }
}
