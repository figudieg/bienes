from rest_framework import serializers
from .models import Inmueble

class InmuebleSerializer(serializers.ModelSerializer):
    sede_nombre = serializers.ReadOnlyField(source='sede.nombre')
    orden_compra_numero = serializers.ReadOnlyField(source='orden_compra.numero_orden')
    asignacion_activa = serializers.SerializerMethodField()

    class Meta:
        model = Inmueble
        fields = '__all__'

    def get_asignacion_activa(self, obj):
        activas = getattr(obj, 'asignaciones_activas', None)
        if activas is not None:
            asignacion = activas[0] if activas else None
        else:
            asignacion = obj.asignaciones.filter(activa=True).select_related('funcionario', 'area').first()
        if not asignacion:
            return None
        return {
            'funcionario_id': asignacion.funcionario_id,
            'funcionario_nombre': asignacion.funcionario.get_full_name() if asignacion.funcionario else None,
            'funcionario_cedula': asignacion.funcionario.cedula if asignacion.funcionario else None,
            'area_nombre': asignacion.area.nombre if asignacion.area else None,
            'fecha_asignacion': asignacion.fecha_asignacion,
        }

    def validate_serial_fabrica(self, value):
        return value if value and value.strip() else None

    def validate_area_terreno(self, value):
        if value <= 0:
            raise serializers.ValidationError("El área del terreno debe ser mayor que cero.")
        return value

    def validate_area_construccion(self, value):
        if value <= 0:
            raise serializers.ValidationError("El área de construcción debe ser mayor que cero.")
        return value
