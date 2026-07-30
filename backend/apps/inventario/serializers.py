from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Sede, Area, OrdenCompra, Bien, Asignacion

User = get_user_model()

class SedeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sede
        fields = '__all__'

class AreaSerializer(serializers.ModelSerializer):
    sede_nombre = serializers.ReadOnlyField(source='sede.nombre')
    
    class Meta:
        model = Area
        fields = '__all__'

class OrdenCompraSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrdenCompra
        fields = '__all__'

class BienSerializer(serializers.ModelSerializer):
    sede_nombre = serializers.ReadOnlyField(source='sede.nombre')
    orden_compra_numero = serializers.ReadOnlyField(source='orden_compra.numero_orden')

    class Meta:
        model = Bien
        fields = '__all__'

    def validate_serial_fabrica(self, value):
        return value if value and value.strip() else None

    def validate_valor_adquisicion(self, value):
        if value < 0:
            raise serializers.ValidationError("El valor de adquisición no puede ser negativo.")
        return value

    def validate_tasa_bcv_compra(self, value):
        if value <= 0:
            raise serializers.ValidationError("La tasa BCV de compra debe ser mayor que cero.")
        return value

    def validate_valor_adquisicion_bs(self, value):
        if value < 0:
            raise serializers.ValidationError("El valor de adquisición en bolívares no puede ser negativo.")
        return value

class AsignacionSerializer(serializers.ModelSerializer):
    bien_codigo = serializers.ReadOnlyField(source='bien.codigo_inventario')
    bien_nombre = serializers.ReadOnlyField(source='bien.nombre')
    usuario_nombre = serializers.ReadOnlyField(source='usuario.get_full_name')
    usuario_cedula = serializers.ReadOnlyField(source='usuario.cedula')
    area_nombre = serializers.ReadOnlyField(source='area.nombre')

    class Meta:
        model = Asignacion
        fields = '__all__'
        extra_kwargs = {
            'area': {'required': False},
        }

    def validate_bien(self, value):
        if Asignacion.objects.filter(bien=value, activa=True).exists():
            raise serializers.ValidationError(
                f'El bien "{value.codigo_inventario}" ya tiene una asignación activa. '
                'Debe reasignarlo desde la lista de asignaciones.'
            )
        return value

    def create(self, validated_data):
        usuario = validated_data.get('usuario')
        if 'area' not in validated_data or validated_data['area'] is None:
            if usuario and usuario.unidad_pertenencia:
                validated_data['area'] = usuario.unidad_pertenencia
            else:
                raise serializers.ValidationError(
                    {'area': 'El usuario no tiene un área asignada. Asigne un área al usuario primero.'}
                )
        return super().create(validated_data)

from .models import TrazabilidadMovimientos

class TrazabilidadSerializer(serializers.ModelSerializer):
    bien_codigo = serializers.ReadOnlyField(source='bien.codigo_inventario')
    bien_nombre = serializers.ReadOnlyField(source='bien.nombre')
    sede_origen_nombre = serializers.ReadOnlyField(source='sede_origen.nombre')
    sede_destino_nombre = serializers.ReadOnlyField(source='sede_destino.nombre')
    area_origen_nombre = serializers.ReadOnlyField(source='area_origen.nombre')
    area_destino_nombre = serializers.ReadOnlyField(source='area_destino.nombre')
    usuario_origen_nombre = serializers.ReadOnlyField(source='usuario_origen.get_full_name')
    usuario_destino_nombre = serializers.ReadOnlyField(source='usuario_destino.get_full_name')
    usuario_responsable_nombre = serializers.ReadOnlyField(source='usuario_responsable.get_full_name')

    class Meta:
        model = TrazabilidadMovimientos
        fields = '__all__'

from .models import MantenimientoBien

class MantenimientoBienSerializer(serializers.ModelSerializer):
    bien_codigo = serializers.ReadOnlyField(source='bien.codigo_inventario')
    bien_nombre = serializers.ReadOnlyField(source='bien.nombre')

    class Meta:
        model = MantenimientoBien
        fields = '__all__'

    def validate_costo(self, value):
        if value < 0:
            raise serializers.ValidationError("El costo del mantenimiento no puede ser negativo.")
        return value

    def validate_reparado_por(self, value):
        if value:
            import re
            value = value.strip()
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\.\(\)\-\,]+$', value):
                raise serializers.ValidationError("El campo 'Reparado por' solo debe contener letras, espacios o signos comunes.")
        return value

    def validate_conformado_por(self, value):
        if value:
            import re
            value = value.strip()
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\.\(\)\-\,]+$', value):
                raise serializers.ValidationError("El campo 'Conformado por' solo debe contener letras, espacios o signos comunes.")
        return value

    def validate_responsable_administrativo(self, value):
        if value:
            import re
            value = value.strip()
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\.\(\)\-\,]+$', value):
                raise serializers.ValidationError("El campo 'Responsable administrativo' solo debe contener letras, espacios o signos comunes.")
        return value