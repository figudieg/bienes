from django.db import models
from apps.inventario.models import Bien

class Automotor(Bien):
    placa = models.CharField(max_length=20, unique=True, verbose_name="Placa del Vehículo")
    marca = models.CharField(max_length=50, verbose_name="Marca")
    modelo = models.CharField(max_length=50, verbose_name="Modelo")
    anio = models.IntegerField(verbose_name="Año de Fabricación")
    color = models.CharField(max_length=30, verbose_name="Color")
    serial_motor = models.CharField(max_length=100, unique=True, verbose_name="Serial del Motor")
    serial_carroceria = models.CharField(max_length=100, unique=True, verbose_name="Serial de Carrocería")

    class Meta:
        db_table = 'automotor'
        verbose_name = 'Automotor'
        verbose_name_plural = 'Automotores'

    def __str__(self):
        return f"Automotor: {self.marca} {self.modelo} - Placa: {self.placa} ({self.codigo_inventario})"
