from django.contrib import admin
from .models import Sede, Area, OrdenCompra, Bien, Asignacion, Funcionario

# ==========================================
# REGISTRO DE MODELOS EN EL PANEL DE ADMIN
# ==========================================

@admin.register(Sede)
class SedeAdmin(admin.ModelAdmin):
    """Configuración para Sede en el panel de administración."""
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    """Configuración para Área en el panel de administración."""
    list_display = ('nombre', 'sede')
    list_filter = ('sede',)
    search_fields = ('nombre', 'sede__nombre')

@admin.register(OrdenCompra)
class OrdenCompraAdmin(admin.ModelAdmin):
    """Configuración para Orden de Compra en el panel de administración."""
    list_display = ('numero_orden', 'fecha_llegada', 'conformidad_recepcion')
    list_filter = ('conformidad_recepcion', 'fecha_llegada')
    search_fields = ('numero_orden',)

@admin.register(Bien)
class BienAdmin(admin.ModelAdmin):
    """Configuración para Bien en el panel de administración."""
    list_display = ('codigo_inventario', 'nombre', 'estado', 'sede')
    list_filter = ('estado', 'sede')
    search_fields = ('codigo_inventario', 'nombre', 'serial_fabrica')

@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ('cedula', 'nombres', 'apellidos', 'cargo', 'area')
    search_fields = ('cedula', 'nombres', 'apellidos')

@admin.register(Asignacion)
class AsignacionAdmin(admin.ModelAdmin):
    """Configuración para Asignación en el panel de administración."""
    list_display = ('bien', 'funcionario', 'area', 'fecha_asignacion', 'activa')
    list_filter = ('activa', 'area', 'fecha_asignacion')
    search_fields = ('bien__codigo_inventario', 'funcionario__cedula', 'funcionario__nombres')