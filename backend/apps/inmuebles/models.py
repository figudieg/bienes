from django.db import models
from apps.inventario.models import Bien

class Inmueble(Bien):
    direccion_completa = models.TextField(verbose_name="Dirección Completa")
    registro_propiedad = models.CharField(max_length=150, unique=True, verbose_name="Registro de Propiedad / Tomo / Folio")
    area_terreno = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Área del Terreno (m²)")
    area_construccion = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Área de Construcción (m²)")
    catastro = models.CharField(max_length=100, unique=True, verbose_name="Ficha Catastral / Número de Catastro")

    class Meta:
        db_table = 'inmueble'
        verbose_name = 'Inmueble'
        verbose_name_plural = 'Inmuebles'

    def __str__(self):
        return f"Inmueble: Catastro {self.catastro} - Registro: {self.registro_propiedad} ({self.codigo_inventario})"
