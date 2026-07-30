from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLES = (
        ('ADMINISTRADOR', 'Administrador'),
        ('AUDITOR', 'Auditor'),
        ('OPERADOR', 'Operador'),
    )

    cedula = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Cédula de Identidad"
    )
    cargo = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Cargo u Oficio"
    )
    unidad_pertenencia = models.ForeignKey(
        'inventario.Area',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Área de Adscripción"
    )
    rol = models.CharField(
        max_length=20,
        choices=ROLES,
        default='OPERADOR',
        verbose_name="Rol en el Sistema"
    )
    reset_code = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        verbose_name="Código de Restablecimiento"
    )
    reset_code_created_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Fecha de Creación del Código"
    )

    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuario del Sistema'
        verbose_name_plural = 'Usuarios del Sistema'

    def __str__(self):
        nombre = self.get_full_name() or self.username
        return f"{self.cedula} - {nombre} ({self.rol})"