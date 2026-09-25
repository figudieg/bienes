from rest_framework import serializers
from .models import LogBien, LogAcceso, Hallazgo

class LogBienSerializer(serializers.ModelSerializer):
    bien_codigo = serializers.ReadOnlyField(source='bien.codigo_inventario')
    usuario_nombre = serializers.ReadOnlyField(source='usuario.username', default='SISTEMA')

    class Meta:
        model = LogBien
        fields = '__all__'

class LogAccesoSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.ReadOnlyField(source='usuario.username', default='SISTEMA')
    usuario_nombre_completo = serializers.ReadOnlyField(source='usuario.get_full_name', default='Sistema Automático')

    class Meta:
        model = LogAcceso
        fields = '__all__'

class HallazgoSerializer(serializers.ModelSerializer):
    bien_codigo = serializers.ReadOnlyField(source='bien.codigo_inventario')
    bien_nombre = serializers.ReadOnlyField(source='bien.nombre')
    gravedad_display = serializers.CharField(source='get_gravedad_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    reportado_por_nombre = serializers.ReadOnlyField(source='reportado_por.username', default=None)
    resuelto_por_nombre = serializers.ReadOnlyField(source='resuelto_por.username', default=None)

    class Meta:
        model = Hallazgo
        fields = '__all__'
        read_only_fields = ['estado', 'reportado_por', 'fecha_resolucion', 'resuelto_por']