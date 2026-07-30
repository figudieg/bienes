from django.core.exceptions import ValidationError
from django.utils import timezone
import re

def validate_rif(value):
    """Valida el formato de RIF venezolano (J-12345678-9 o J123456789)"""
    pattern = r'^[G|J|V|E|P][-|]?\d{8}[-|]?\d$'
    if not re.match(pattern, value):
        raise ValidationError(
            'El formato del RIF es inválido. Ejemplo: J-12345678-9'
        )

def validate_cedula(value):
    """Valida formato de cédula venezolana (V-12345678 o E-12345678)"""
    pattern = r'^[V|E][-|]?\d{6,8}$'
    if not re.match(pattern, value):
        raise ValidationError(
            'Formato de cédula inválido. Use V-12345678 o E-12345678'
        )

def validate_telefono(value):
    """Valida formato de teléfono (04141234567 o 02121234567)"""
    pattern = r'^(0414|0424|0412|0416|0426|0212)\d{7}$'
    if not re.match(pattern, value):
        raise ValidationError(
            'Número de teléfono inválido. Debe empezar por 04XX o 02XX y tener 11 dígitos.'
        )

def validate_solo_numeros(value):
    """Asegura que el campo solo contenga dígitos"""
    if not value.isdigit():
        raise ValidationError('Este campo solo debe contener números.')
    
def validate_fecha_no_pasada(value):
    """Impide registrar fechas anteriores al día de hoy"""
    if value < timezone.now().date():
        raise ValidationError(
            f'La fecha no puede ser anterior al día de hoy ({timezone.now().date()}).'
        )
