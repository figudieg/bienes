from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Personaliza la respuesta del Login para que Angular 
    tenga toda la info del usuario y su rol.
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        data['user'] = {
            'id': user.id,
            'username': user.username,
            'full_name': user.get_full_name() or user.username,
            'email': user.email,
            'rol': user.rol,
            'cedula': user.cedula,
            'cargo': user.cargo,
            'unidad_pertenencia_id': user.unidad_pertenencia_id if user.unidad_pertenencia else None,
            'is_active': user.is_active
        }
        return data

class UserSerializer(serializers.ModelSerializer):
    unidad_nombre = serializers.ReadOnlyField(source='unidad_pertenencia.nombre')

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'cedula', 'cargo', 'rol', 'unidad_pertenencia', 'unidad_nombre', 'is_active', 'password'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def validate_cedula(self, value):
        value = value.strip().upper()
        # Si contiene solo dígitos, por defecto ponemos el prefijo V-
        if value.isdigit():
            value = f"V-{value}"
        # Si tiene formato V12345678, agregamos el guión
        import re
        if re.match(r'^[V|E]\d{6,8}$', value):
            value = f"{value[0]}-{value[1:]}"
            
        pattern = r'^[V|E]-\d{6,8}$'
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                'Formato de cédula inválido. Debe ser como V-12345678 o E-12345678.'
            )
        return value

    def validate_first_name(self, value):
        if value:
            import re
            value = value.strip()
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', value):
                raise serializers.ValidationError('El nombre solo debe contener letras y espacios.')
        return value

    def validate_last_name(self, value):
        if value:
            import re
            value = value.strip()
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', value):
                raise serializers.ValidationError('El apellido solo debe contener letras y espacios.')
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance