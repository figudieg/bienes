from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.auditoria.models import LogAcceso
from django.utils import timezone
import datetime

class Command(BaseCommand):
    help = 'Seeds database with default users, roles, and session access logs'

    def handle(self, *args, **options):
        User = get_user_model()
        users_data = [
            {
                'username': 'admin',
                'password': 'Password123!',
                'cedula': 'V-11111111',
                'first_name': 'Carlos',
                'last_name': 'Administrador',
                'email': 'admin@sudevip.local',
                'rol': 'ADMINISTRADOR',
                'is_superuser': True,
                'is_staff': True
            },
            {
                'username': 'auditor',
                'password': 'Password123!',
                'cedula': 'V-22222222',
                'first_name': 'María',
                'last_name': 'Auditora',
                'email': 'auditor@sudevip.local',
                'rol': 'AUDITOR',
            },
            {
                'username': 'operador',
                'password': 'Password123!',
                'cedula': 'V-33333333',
                'first_name': 'Juan',
                'last_name': 'Operador',
                'email': 'operador@sudevip.local',
                'rol': 'OPERADOR',
            }
        ]

        self.stdout.write("Creando usuarios de prueba...")
        for u_data in users_data:
            username = u_data.pop('username')
            password = u_data.pop('password')
            
            # Buscamos por username, actualizando datos
            user, created = User.objects.get_or_create(username=username, defaults=u_data)
            if created or not user.check_password(password):
                user.set_password(password)
                for k, v in u_data.items():
                    setattr(user, k, v)
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Usuario {username} {'creado' if created else 'actualizado'}."))
            else:
                self.stdout.write(self.style.WARNING(f"Usuario {username} ya existe."))
        
        # Limpiar accesos previos para evitar duplicación masiva en semillas continuas
        LogAcceso.objects.all().delete()
        self.stdout.write("Creando registros de acceso de prueba (Control Interno)...")
        
        # Obtenemos usuarios reales creados
        u_admin = User.objects.get(username='admin')
        u_auditor = User.objects.get(username='auditor')
        u_operador = User.objects.get(username='operador')

        # Creamos logs de accesos con diferentes IPs y detalles
        logs_acceso = [
            LogAcceso(usuario=u_admin, ip_address='192.168.1.12', accion='INICIO_SESION', detalles='Inicio de sesión exitoso desde el panel administrativo.'),
            LogAcceso(usuario=u_admin, ip_address='192.168.1.12', accion='MODIFICACION_CLAVE', detalles='El usuario administrador cambió su clave de seguridad.'),
            LogAcceso(usuario=u_auditor, ip_address='192.168.2.45', accion='INICIO_SESION', detalles='Inicio de sesión exitoso de especialista para auditoría patrimonial.'),
            LogAcceso(usuario=u_operador, ip_address='192.168.10.150', accion='INICIO_SESION', detalles='Inicio de sesión exitoso del operador de inventario de guardia.'),
            LogAcceso(usuario=u_operador, ip_address='192.168.10.150', accion='REGISTRO_BIEN', detalles='Operador incorporó un nuevo bien al catálogo de la DEM.'),
            LogAcceso(usuario=u_auditor, ip_address='172.16.8.90', accion='INICIO_SESION', detalles='Auditor se conectó de forma remota vía VPN institucional.'),
            LogAcceso(usuario=u_admin, ip_address='10.0.0.5', accion='CIERRE_SESION', detalles='Cierre de sesión manual ejecutado correctamente.'),
        ]
        
        LogAcceso.objects.bulk_create(logs_acceso)
        self.stdout.write(self.style.SUCCESS("Semillas de control de acceso creadas con éxito."))
        self.stdout.write(self.style.SUCCESS("Completado con éxito."))
