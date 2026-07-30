from django.contrib import admin
from .models import LogBien

@admin.register(LogBien)
class LogBienAdmin(admin.ModelAdmin):
    """
    Panel de administración para los Logs de Bienes.
    Bloqueado para solo lectura, asegurando la integridad de la auditoría.
    """
    list_display = ('fecha', 'usuario', 'bien', 'accion')
    list_filter = ('accion', 'fecha')
    search_fields = ('bien__codigo_inventario', 'usuario__username')
    
    # Bloqueamos todos los campos para que no puedan ser editados
    readonly_fields = ('bien', 'usuario', 'accion', 'fecha', 'detalles')
    
    def has_add_permission(self, request):
        """Impide crear logs manualmente desde el admin."""
        return False

    def has_change_permission(self, request, obj=None):
        """Impide editar logs existentes."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Impide borrar los registros de auditoría."""
        return False