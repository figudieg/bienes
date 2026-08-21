from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Sede, Area, OrdenCompra, Bien, Asignacion, Funcionario

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

class FuncionarioSerializer(serializers.ModelSerializer):
    area_nombre = serializers.ReadOnlyField(source='area.nombre')
    
    class Meta:
        model = Funcionario
        fields = '__all__'

class BienSerializer(serializers.ModelSerializer):
    sede_nombre = serializers.ReadOnlyField(source='sede.nombre')
    orden_compra_numero = serializers.ReadOnlyField(source='orden_compra.numero_orden')
    asignacion_activa = serializers.SerializerMethodField()
    tipo = serializers.SerializerMethodField()
    categoria_display = serializers.CharField(source='get_categoria_display', read_only=True)

    class Meta:
        model = Bien
        fields = '__all__'

    def get_tipo(self, obj):
        if hasattr(obj, 'automotor'):
            return 'AUTOMOTOR'
        if hasattr(obj, 'inmueble'):
            return 'INMUEBLE'
        return 'MUEBLE'

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
            'funcionario_nombre': f"{asignacion.funcionario.nombres} {asignacion.funcionario.apellidos}" if asignacion.funcionario else 'Sin asignar',
            'funcionario_cedula': asignacion.funcionario.cedula if asignacion.funcionario else None,
            'area_id': asignacion.area_id,
            'area_nombre': asignacion.area.nombre if asignacion.area else None,
            'direccion_general': asignacion.area.direccion_general if asignacion.area else None,
            'fecha_asignacion': asignacion.fecha_asignacion,
        }

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
    funcionario_nombre = serializers.SerializerMethodField()
    funcionario_cedula = serializers.ReadOnlyField(source='funcionario.cedula')
    area_nombre = serializers.ReadOnlyField(source='area.nombre')

    def get_funcionario_nombre(self, obj):
        if obj.funcionario:
            return f"{obj.funcionario.nombres} {obj.funcionario.apellidos}"
        return "Sin Asignar"

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
        funcionario = validated_data.get('funcionario')
        if 'area' not in validated_data or validated_data['area'] is None:
            if funcionario and funcionario.area:
                validated_data['area'] = funcionario.area
            else:
                raise serializers.ValidationError(
                    {'area': 'El funcionario no tiene un área asignada. Especifique el área o asigne una al funcionario primero.'}
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
    funcionario_origen_nombre = serializers.SerializerMethodField()
    funcionario_destino_nombre = serializers.SerializerMethodField()
    usuario_responsable_nombre = serializers.ReadOnlyField(source='usuario_responsable.get_full_name')

    def get_funcionario_origen_nombre(self, obj):
        return f"{obj.funcionario_origen.nombres} {obj.funcionario_origen.apellidos}" if obj.funcionario_origen else None

    def get_funcionario_destino_nombre(self, obj):
        return f"{obj.funcionario_destino.nombres} {obj.funcionario_destino.apellidos}" if obj.funcionario_destino else None
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