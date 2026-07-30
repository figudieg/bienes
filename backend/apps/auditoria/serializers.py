from rest_framework import serializers
from .models import LogBien, LogAcceso

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