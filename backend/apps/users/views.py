import re
import unicodedata

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer, UserSerializer

User = get_user_model()


def _normalizar_nombre_oficina(texto):
    """Mayúsculas, sin tildes ni paréntesis, espacios colapsados — para poder
    comparar el texto libre de SISCOM contra el nombre real de una Area."""
    if not texto:
        return ''
    texto = re.sub(r'\([^)]*\)', ' ', texto)
    sin_tildes = ''.join(
        c for c in unicodedata.normalize('NFKD', texto) if not unicodedata.combining(c)
    )
    return re.sub(r'\s{2,}', ' ', sin_tildes).strip().upper()

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Endpoint principal de Login (JWT) con rol incluido.
    """
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

class UserViewSet(viewsets.ModelViewSet):
    """
    API para gestión de usuarios.
    """
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['create', 'forgot_credentials', 'verify_code', 'reset_credentials']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='buscar-por-cedula', permission_classes=[IsAuthenticated])
    def buscar_por_cedula(self, request):
        """
        Busca un usuario por su número de cédula.
        Retorna datos completos: nombre, cargo, área, etc.
        Uso: GET /api/users/gestion/buscar-por-cedula/?cedula=12345678
        """
        from django.db.models import Q
        cedula = request.query_params.get('cedula', '').strip()
        if not cedula:
            return Response(
                {'error': 'Debe proporcionar un número de cédula.'},
                status=400
            )
        try:
            # Búsqueda inteligente: si es numérico, busca la cédula exacta o con prefijos V- / E-
            if cedula.isdigit():
                usuario = User.objects.select_related('unidad_pertenencia', 'unidad_pertenencia__sede').filter(
                    Q(cedula=cedula) | Q(cedula=f"V-{cedula}") | Q(cedula=f"E-{cedula}")
                ).first()
                if not usuario:
                    raise User.DoesNotExist()
            else:
                usuario = User.objects.select_related('unidad_pertenencia', 'unidad_pertenencia__sede').get(cedula=cedula)
        except User.DoesNotExist:
            return Response(
                {'error': f'No se encontró un usuario con la cédula {cedula}.'},
                status=404
            )
        
        data = {
            'id': usuario.id,
            'cedula': usuario.cedula,
            'nombre_completo': usuario.get_full_name() or usuario.username,
            'first_name': usuario.first_name,
            'last_name': usuario.last_name,
            'email': usuario.email,
            'cargo': usuario.cargo or '—',
            'rol': usuario.rol,
            'unidad_pertenencia_id': usuario.unidad_pertenencia_id,
            'unidad_pertenencia_nombre': usuario.unidad_pertenencia.nombre if usuario.unidad_pertenencia else '—',
            'sede_nombre': usuario.unidad_pertenencia.sede.nombre if usuario.unidad_pertenencia and usuario.unidad_pertenencia.sede else '—',
            'is_active': usuario.is_active,
        }
        return Response(data)

    @action(detail=False, methods=['get'], url_path='consultar-cedula', permission_classes=[IsAuthenticated])
    def consultar_cedula(self, request):
        """
        Consulta los datos actualizados de un funcionario en el sistema SISCOM
        del DEM (http://wssiscom.dem.int/evaluacion/<cedula>) y sincroniza el
        registro local de Funcionario (directorio de personas a quienes se les
        puede asignar bienes; no tiene login ni relación con las cuentas de
        usuario del sistema).
        Uso: GET /api/users/gestion/consultar-cedula/?cedula=12345678
        """
        import json
        import urllib.error
        import urllib.request
        from django.conf import settings
        from django.db.models import Q
        from apps.inventario.models import Funcionario, Area

        cedula = request.query_params.get('cedula', '').strip()
        if not cedula or not cedula.isdigit():
            return Response({'error': 'Debe proporcionar un número de cédula válido.'}, status=400)

        url = f"{settings.WSSISCOM_EVALUACION_URL.rstrip('/')}/{cedula}"
        try:
            with urllib.request.urlopen(url, timeout=6) as resp:
                payload = json.loads(resp.read().decode('utf-8'))
        except urllib.error.URLError:
            return Response(
                {'error': 'No se pudo conectar con el sistema de RRHH (SISCOM). Verifique la red del DEM e intente nuevamente.'},
                status=502
            )
        except ValueError:
            return Response({'error': 'El sistema de RRHH devolvió una respuesta inválida.'}, status=502)

        datos = payload.get('sigefirrhh') if isinstance(payload, dict) else None
        if not datos or not datos.get('cedula'):
            return Response(
                {'error': f'No se encontró un funcionario con la cédula {cedula} en el sistema de RRHH.'},
                status=404
            )

        nombre_completo = (datos.get('nombres') or '').strip()
        cargo = datos.get('descripcion_cargo')
        dependencia = datos.get('nombre')

        funcionario_data = {
            'cedula': datos.get('cedula'),
            'nombre_completo': nombre_completo,
            'cargo': cargo,
            'dependencia': dependencia,
            'categoria': datos.get('desc_categoria'),
            'tipo_relacion': datos.get('desc_relacion'),
            'tipo_personal': datos.get('tipo_personal'),
            'grado': datos.get('grado'),
            'fecha_ingreso': datos.get('fecha_ingreso'),
        }

        # Divide el nombre completo (SISCOM lo entrega como un solo campo) en
        # nombres/apellidos de forma aproximada, para mantener sincronizado el
        # directorio local de Funcionario con los datos frescos de RRHH.
        palabras = nombre_completo.split()
        mitad = max(1, (len(palabras) + 1) // 2)
        nombres = ' '.join(palabras[:mitad]) or nombre_completo
        apellidos = ' '.join(palabras[mitad:]) or nombres

        existente = Funcionario.objects.filter(
            Q(cedula=cedula) | Q(cedula=f"V-{cedula}") | Q(cedula=f"E-{cedula}")
        ).first()
        cedula_funcionario = existente.cedula if existente else f"V-{cedula}"

        # Intenta ubicar la oficina real (cargada desde la Convalidación de
        # Oficinas) a partir del texto libre que entrega SISCOM en "nombre"
        # (ej. "OFICINA DE DESARROLLO INFORMATICO - DIRECCION EJECUTIVA...").
        area_match = None
        if dependencia:
            segmento = dependencia.split(' - ')[0]
            segmento_norm = _normalizar_nombre_oficina(segmento)
            for area in Area.objects.filter(activa=True):
                if _normalizar_nombre_oficina(area.nombre) == segmento_norm:
                    area_match = area
                    break

        defaults = {'nombres': nombres, 'apellidos': apellidos, 'cargo': cargo}
        if area_match:
            defaults['area'] = area_match

        funcionario, _ = Funcionario.objects.update_or_create(
            cedula=cedula_funcionario,
            defaults=defaults,
        )

        return Response({
            'funcionario': funcionario_data,
            'funcionario_id': funcionario.id,
            'area_id': funcionario.area_id,
            'area_nombre': funcionario.area.nombre if funcionario.area else None,
        })

    @action(detail=False, methods=['post'], url_path='forgot-credentials', permission_classes=[AllowAny])
    def forgot_credentials(self, request):
        """
        Genera un código de 6 dígitos para el usuario según su username.
        POST /api/users/gestion/forgot-credentials/
        Body: {"username": "usuario_ejemplo"}
        """
        import random
        from django.utils import timezone
        
        username = request.data.get('username', '').strip()
        if not username:
            return Response({'error': 'Debe proporcionar un nombre de usuario.'}, status=400)
            
        try:
            usuario = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'No existe ningún usuario registrado con ese nombre de usuario.'}, status=404)
            
        # Generar código OTP de 6 dígitos
        code = f"{random.randint(100000, 999999)}"
        usuario.reset_code = code
        usuario.reset_code_created_at = timezone.now()
        usuario.save()
        
        # Enviar correo de respaldo si está configurado (de lo contrario se almacena para el admin)
        from django.core.mail import send_mail
        if usuario.email:
            subject = 'Recuperación de Credenciales - SUDEVIP'
            message = f"""
Hola, {usuario.get_full_name() or usuario.username}.

Has solicitado la recuperación de tus credenciales para SUDEVIP.

Tus datos de recuperación son:
----------------------------------------------
* Nombre de Usuario: {usuario.username}
* Código de Verificación OTP: {code}
----------------------------------------------

El administrador del sistema también tiene acceso a este código si no puede revisar su correo.
Este código expirará en 15 minutos.
"""
            try:
                send_mail(
                    subject,
                    message,
                    None,
                    [usuario.email],
                    fail_silently=True,
                )
            except Exception:
                pass
                
        return Response({'message': 'Solicitud registrada. Por favor solicite el código de verificación al Administrador.'})

    @action(detail=False, methods=['post'], url_path='verify-code', permission_classes=[AllowAny])
    def verify_code(self, request):
        """
        Verifica que el código ingresado para el usuario sea válido.
        POST /api/users/gestion/verify-code/
        Body: {"username": "usuario_ejemplo", "code": "123456"}
        """
        from django.utils import timezone
        
        username = request.data.get('username', '').strip()
        code = request.data.get('code', '').strip()
        
        if not username or not code:
            return Response({'error': 'Debe proporcionar el usuario y el código de verificación.'}, status=400)
            
        try:
            usuario = User.objects.get(username=username, reset_code=code)
        except User.DoesNotExist:
            return Response({'error': 'El código de verificación es incorrecto.'}, status=400)
            
        # Verificar expiración (15 minutos)
        if usuario.reset_code_created_at:
            diff = timezone.now() - usuario.reset_code_created_at
            if diff.total_seconds() > 900:
                return Response({'error': 'El código de verificación ha expirado. Solicite uno nuevo.'}, status=400)
                
        return Response({
            'message': 'Código verificado con éxito.',
            'username': usuario.username
        })

    @action(detail=False, methods=['post'], url_path='reset-credentials', permission_classes=[AllowAny])
    def reset_credentials(self, request):
        """
        Restablece la contraseña si el código es válido.
        POST /api/users/gestion/reset-credentials/
        Body: {"username": "usuario_ejemplo", "code": "123456", "new_password": "NewPassword123!"}
        """
        from django.utils import timezone
        
        username = request.data.get('username', '').strip()
        code = request.data.get('code', '').strip()
        new_password = request.data.get('new_password', '').strip()
        
        if not username or not code or not new_password:
            return Response({'error': 'Todos los campos son obligatorios.'}, status=400)
            
        try:
            usuario = User.objects.get(username=username, reset_code=code)
        except User.DoesNotExist:
            return Response({'error': 'Código de verificación inválido.'}, status=400)
            
        # Verificar expiración (15 minutos)
        if usuario.reset_code_created_at:
            diff = timezone.now() - usuario.reset_code_created_at
            if diff.total_seconds() > 900:
                return Response({'error': 'El código de verificación ha expirado.'}, status=400)
                
        # Restablecer contraseña y limpiar código
        usuario.set_password(new_password)
        usuario.reset_code = None
        usuario.reset_code_created_at = None
        usuario.save()
        
        return Response({'message': 'Contraseña restablecida con éxito.'})

    @action(detail=False, methods=['get'], url_path='recovery-requests', permission_classes=[IsAuthenticated])
    def recovery_requests(self, request):
        """
        Devuelve el listado de solicitudes de recuperación con sus códigos OTP.
        Solo accesible para el rol de ADMINISTRADOR.
        """
        if request.user.rol != 'ADMINISTRADOR':
            return Response({'error': 'Acceso denegado. Se requieren privilegios de Administrador.'}, status=403)
            
        usuarios = User.objects.filter(reset_code__isnull=False).exclude(reset_code='').order_by('-reset_code_created_at')
        
        data = []
        for u in usuarios:
            data.append({
                'username': u.username,
                'nombre_completo': u.get_full_name() or u.username,
                'cedula': u.cedula,
                'reset_code': u.reset_code,
                'reset_code_created_at': u.reset_code_created_at
            })
            
        return Response(data)