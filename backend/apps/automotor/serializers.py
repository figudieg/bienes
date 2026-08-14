from rest_framework import serializers
from .models import Automotor

class AutomotorSerializer(serializers.ModelSerializer):
    sede_nombre = serializers.ReadOnlyField(source='sede.nombre')
    orden_compra_numero = serializers.ReadOnlyField(source='orden_compra.numero_orden')
    asignacion_activa = serializers.SerializerMethodField()

    class Meta:
        model = Automotor
        fields = '__all__'

    def get_asignacion_activa(self, obj):
        activas = getattr(obj, 'asignaciones_activas', None)
        if activas is not None:
            asignacion = activas[0] if activas else None
        else:
            asignacion = obj.asignaciones.filter(activa=True).select_related('usuario', 'area').first()
        if not asignacion:
            return None
        return {
            'usuario_id': asignacion.usuario_id,
            'usuario_nombre': asignacion.usuario.get_full_name() or asignacion.usuario.username,
            'usuario_cedula': asignacion.usuario.cedula,
            'area_nombre': asignacion.area.nombre if asignacion.area else None,
            'fecha_asignacion': asignacion.fecha_asignacion,
        }

    def validate_serial_fabrica(self, value):
        return value if value and value.strip() else None

    def validate_serial_motor(self, value):
        return value if value and value.strip() else None

    def validate_serial_carroceria(self, value):
        return value if value and value.strip() else None

    def validate_anio(self, value):
        if value < 1900 or value > 2100:
            raise serializers.ValidationError("El año de fabricación debe ser un año válido (entre 1900 y 2100).")
        return value

    def validate_marca(self, value):
        if value:
            import re
            value = value.strip()
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\-]+$', value):
                raise serializers.ValidationError("La marca solo debe contener letras, espacios o guiones.")
        return value

    def validate_color(self, value):
        if value:
            import re
            value = value.strip()
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', value):
                raise serializers.ValidationError("El color solo debe contener letras y espacios.")
        return value
