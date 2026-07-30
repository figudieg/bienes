from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.inventario.models import Sede, Bien
from .models import LogBien

User = get_user_model()

class AuditoriaAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass',
            cedula='V-88888888',
            rol='AUDITOR'
        )
        self.client.force_authenticate(user=self.user)

        self.sede = Sede.objects.create(nombre='Sede Principal')
        
        # Al crear este Bien, la signal registrar_auditoria_bien se ejecutará
        # y creará un LogBien automáticamente.
        self.bien = Bien.objects.create(
            nombre='Computadora HP EliteDesk',
            descripcion='Intel i7, 16GB RAM',
            codigo_inventario='DEM-PC-001',
            sede=self.sede
        )

    def test_auditoria_list(self):
        response = self.client.get('/api/auditoria/logs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Debería haber 1 log creado por la signal de creación de Bien
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['accion'], 'CREACION')
        self.assertIn('DEM-PC-001', response.data[0]['detalles'])
