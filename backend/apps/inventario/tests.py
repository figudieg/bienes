from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date
from .models import Sede, Area, OrdenCompra, Bien, Asignacion

User = get_user_model()

class InventarioAPITestCase(APITestCase):
    def setUp(self):
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass',
            cedula='V-77777777',
            rol='ADMINISTRADOR'
        )
        self.client.force_authenticate(user=self.user)

        # Crear datos de prueba
        self.sede = Sede.objects.create(nombre='Sede Principal')
        self.area = Area.objects.create(sede=self.sede, nombre='Departamento de TI')
        
        self.orden = OrdenCompra.objects.create(
            numero_orden='ORD-2026-0001',
            fecha_llegada=date(2026, 4, 1),
            conformidad_recepcion=True
        )
        
        self.bien = Bien.objects.create(
            nombre='Servidor Dell PowerEdge',
            descripcion='Intel Xeon, 64GB RAM, 2TB SSD',
            serial_fabrica='SN-DELL-XYZ123',
            codigo_inventario='DEM-SERV-001',
            estado='ACTIVO',
            sede=self.sede,
            orden_compra=self.orden,
            valor_adquisicion=Decimal('2500.00'),
            tasa_bcv_compra=Decimal('36.5000'),
            valor_adquisicion_bs=Decimal('91250.00')
        )
        
        self.asignacion = Asignacion.objects.create(
            bien=self.bien,
            usuario=self.user,
            area=self.area,
            activa=True
        )

    def test_sedes_list(self):
        response = self.client.get('/api/inventario/sedes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nombre'], 'Sede Principal')

    def test_areas_list(self):
        response = self.client.get('/api/inventario/areas/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nombre'], 'Departamento de TI')

    def test_ordenes_list(self):
        response = self.client.get('/api/inventario/ordenes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['numero_orden'], 'ORD-2026-0001')

    def test_bienes_list(self):
        response = self.client.get('/api/inventario/bienes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['codigo_inventario'], 'DEM-SERV-001')

    def test_orden_reporte_pdf(self):
        response = self.client.get(f'/api/inventario/ordenes/{self.orden.id}/reporte-pdf/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
