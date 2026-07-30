from rest_framework import serializers
from .models import Inmueble

class InmuebleSerializer(serializers.ModelSerializer):
    sede_nombre = serializers.ReadOnlyField(source='sede.nombre')
    orden_compra_numero = serializers.ReadOnlyField(source='orden_compra.numero_orden')

    class Meta:
        model = Inmueble
        fields = '__all__'

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
