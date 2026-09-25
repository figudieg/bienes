/** Solo letras (con acentos/ñ) y espacios — para nombres, apellidos, marca, color. */
export const PATRON_SOLO_LETRAS = /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/;

/** Letras, espacios y signos comunes de cargos/títulos (. ( ) - ,) — para "Ing. Pérez (Soporte)". */
export const PATRON_NOMBRE_CON_TITULO = /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s.()\-,]+$/;

/** Letras, espacios y "/" — para material/color combinados como "Metal/Tela". */
export const PATRON_LETRAS_CON_BARRA = /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s/]+$/;

/** Exige que el texto tenga al menos una letra (rechaza códigos puramente numéricos). */
export const PATRON_CONTIENE_LETRA = /[a-zA-ZáéíóúÁÉÍÓÚñÑ]/;

/** Solo dígitos — para cédulas de identidad. */
export const PATRON_SOLO_DIGITOS = /^[0-9]+$/;

export function esSoloDigitos(valor: string | null | undefined): boolean {
  if (!valor || !valor.trim()) return false;
  return PATRON_SOLO_DIGITOS.test(valor.trim());
}

export function esSoloLetras(valor: string | null | undefined): boolean {
  if (!valor || !valor.trim()) return false;
  return PATRON_SOLO_LETRAS.test(valor.trim());
}

export function esNombreConTitulo(valor: string | null | undefined): boolean {
  if (!valor || !valor.trim()) return false;
  return PATRON_NOMBRE_CON_TITULO.test(valor.trim());
}
