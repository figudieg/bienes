import os
import random
from datetime import date
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.inventario.models import Sede, Area, OrdenCompra, Bien, Asignacion, TrazabilidadMovimientos
from apps.automotor.models import Automotor
from apps.inmuebles.models import Inmueble

class Command(BaseCommand):
    help = 'Seeds database with massive test data (3 purchase orders with 50 assets each: IT, Vehicles, and Real Estate)'

    def handle(self, *args, **options):
        User = get_user_model()
        
        self.stdout.write("Iniciando purga de datos antiguos para comenzar limpio...")
        # Eliminamos datos existentes de bienes y ordenes para evitar duplicados y colisiones
        Asignacion.objects.all().delete()
        TrazabilidadMovimientos.objects.all().delete()
        Inmueble.objects.all().delete()
        Automotor.objects.all().delete()
        Bien.objects.all().delete()
        OrdenCompra.objects.all().delete()
        
        self.stdout.write("Creando Sedes y Áreas de respaldo si no existen...")
        sede_central, _ = Sede.objects.get_or_create(nombre='Sede Principal (DEM - Caracas)')
        sede_regional, _ = Sede.objects.get_or_create(nombre='Dirección Regional de la Magistratura (Edo. Miranda)')
        
        area_ti, _ = Area.objects.get_or_create(sede=sede_central, nombre='Dirección de Tecnología y Sistemas (TI)')
        area_trans, _ = Area.objects.get_or_create(sede=sede_central, nombre='Coordinación de Transporte y Logística')
        area_admin, _ = Area.objects.get_or_create(sede=sede_regional, nombre='División Administrativa y Servicios Generales')

        # Obtenemos usuarios
        u_admin = User.objects.filter(rol='ADMINISTRADOR').first()
        u_auditor = User.objects.filter(rol='AUDITOR').first()
        u_operador = User.objects.filter(rol='OPERADOR').first()
        
        if not u_admin or not u_auditor or not u_operador:
            self.stdout.write(self.style.ERROR("Error: Usuarios de prueba no encontrados. Por favor corre primero: python manage.py seed_users"))
            return

        # --- ORDEN 1: EQUIPOS INFORMÁTICOS (50 Bienes) ---
        self.stdout.write("Generando Orden de Compra 1: Equipos Informáticos (50 lotes)...")
        oc_it = OrdenCompra.objects.create(
            numero_orden='OC-IT-2026-001',
            proveedor='Equipos y Soluciones Tecnológicas Corporativas S.A.',
            fecha_llegada=date(2026, 1, 15),
            conformidad_recepcion=True
        )
        
        it_names = [
            ('Computadora HP EliteDesk G9', 'Mini PC, Intel i7, 16GB RAM, 512GB SSD'),
            ('Servidor Rack Dell PowerEdge R760', 'Xeon 24 Cores, 128GB RAM, 4TB SSD SAS'),
            ('Laptop Lenovo ThinkPad L14', 'Pantalla 14 pulgadas, Ryzen 5, 16GB, 512GB'),
            ('Impresora Kyocera Ecosys M3655', 'Multifuncional monocromático de alto rendimiento'),
            ('Punto de Acceso Cisco Catalyst 9120', 'Wi-Fi 6 corporativo de alta densidad')
        ]
        
        for i in range(1, 51):
            name, desc = random.choice(it_names)
            codigo = f"DEM-INF-{1000 + i}"
            serial = f"S/N-INF-88{8000 + i}"
            # Mezclar estados 70% asignado (ACTIVO), 25% sin asignar (INACTIVO), 5% desincorporado
            rand_val = random.random()
            estado = 'ACTIVO' if rand_val < 0.70 else ('INACTIVO' if rand_val < 0.95 else 'DESINCORPORADO')
            
            valor = Decimal(f"{random.randint(200, 4500)}.00")
            bcv = Decimal("36.50")
            valor_bs = valor * bcv

            bien = Bien.objects.create(
                nombre=f"{name} #{i}",
                descripcion=f"{desc}. Lote de fiscalización. Registro individual.",
                serial_fabrica=serial,
                codigo_inventario=codigo,
                estado=estado,
                sede=sede_central,
                orden_compra=oc_it,
                valor_adquisicion=valor,
                tasa_bcv_compra=bcv,
                valor_adquisicion_bs=valor_bs
            )
            
            # Registrar Trazabilidad Inicial
            TrazabilidadMovimientos.objects.create(
                bien=bien,
                tipo_movimiento='INCORPORACION',
                sede_destino=sede_central,
                area_destino=area_ti,
                usuario_destino=u_operador,
                motivo='Ingreso masivo al inventario informático de la DEM.',
                usuario_responsable=u_admin
            )

            # Asignar usuario si está ACTIVO
            if estado == 'ACTIVO':
                u_target = random.choice([u_admin, u_auditor, u_operador])
                Asignacion.objects.create(
                    bien=bien,
                    usuario=u_target,
                    area=area_ti,
                    activa=True
                )
                
                TrazabilidadMovimientos.objects.create(
                    bien=bien,
                    tipo_movimiento='ASIGNACION',
                    sede_origen=sede_central,
                    sede_destino=sede_central,
                    area_origen=area_ti,
                    area_destino=area_ti,
                    usuario_destino=u_target,
                    motivo=f'Asignación física directa al funcionario @{u_target.username} para labores técnicas.',
                    usuario_responsable=u_admin
                )

        # --- ORDEN 2: PARQUE AUTOMOTOR (50 Automotores) ---
        self.stdout.write("Generando Orden de Compra 2: Parque Automotor (50 vehículos)...")
        oc_veh = OrdenCompra.objects.create(
            numero_orden='OC-VEH-2026-002',
            proveedor='Corporación de Transporte Automotriz del Centro C.A.',
            fecha_llegada=date(2026, 2, 10),
            conformidad_recepcion=True
        )
        
        veh_brands = [
            ('Toyota', 'Corolla', 2024),
            ('Toyota', 'Hilux Double Cab', 2025),
            ('Chevrolet', 'Spark GT', 2023),
            ('Chevrolet', 'Cruze', 2024),
            ('Ford', 'Explorer Limited', 2024)
        ]
        colors_list = ['Blanco Celta', 'Gris Metálico', 'Azul Marino', 'Negro Obsidiana', 'Plata Brillante']
        
        for i in range(1, 51):
            brand, model, anio = random.choice(veh_brands)
            color = random.choice(colors_list)
            placa = f"DEM-{i:03d}AA"
            codigo = f"DEM-VEH-{2000 + i}"
            serial_fab = f"VIN-AUTOMOTOR-99{9000 + i}"
            
            rand_val = random.random()
            estado = 'ACTIVO' if rand_val < 0.75 else ('INACTIVO' if rand_val < 0.95 else 'DESINCORPORADO')
            
            valor = Decimal(f"{random.randint(12000, 48000)}.00")
            bcv = Decimal("36.50")
            valor_bs = valor * bcv

            auto = Automotor.objects.create(
                nombre=f"Vehículo {brand} {model} ({placa})",
                descripcion=f"Automotor institucional. Color: {color}. Año: {anio}.",
                serial_fabrica=serial_fab,
                codigo_inventario=codigo,
                estado=estado,
                sede=sede_central,
                orden_compra=oc_veh,
                valor_adquisicion=valor,
                tasa_bcv_compra=bcv,
                valor_adquisicion_bs=valor_bs,
                placa=placa,
                marca=brand,
                modelo=model,
                anio=anio,
                color=color,
                serial_motor=f"MOT-{placa}-{random.randint(1000,9999)}",
                serial_carroceria=f"CARR-{placa}-{random.randint(1000,9999)}"
            )

            TrazabilidadMovimientos.objects.create(
                bien=auto,
                tipo_movimiento='INCORPORACION',
                sede_destino=sede_central,
                area_destino=area_trans,
                usuario_destino=u_operador,
                motivo='Incorporación física al parque automotor de la DEM.',
                usuario_responsable=u_admin
            )

            if estado == 'ACTIVO':
                u_target = random.choice([u_admin, u_auditor, u_operador])
                Asignacion.objects.create(
                    bien=auto,
                    usuario=u_target,
                    area=area_trans,
                    activa=True
                )
                
                TrazabilidadMovimientos.objects.create(
                    bien=auto,
                    tipo_movimiento='ASIGNACION',
                    sede_origen=sede_central,
                    sede_destino=sede_central,
                    area_origen=area_trans,
                    area_destino=area_trans,
                    usuario_destino=u_target,
                    motivo=f'Asignación del vehículo institucional para traslados y comisiones al funcionario @{u_target.username}.',
                    usuario_responsable=u_admin
                )

        # --- ORDEN 3: BIENES INMUEBLES (50 Inmuebles) ---
        self.stdout.write("Generando Orden de Compra 3: Bienes Inmuebles (50 inmuebles)...")
        oc_inm = OrdenCompra.objects.create(
            numero_orden='OC-INM-2026-003',
            proveedor='Donaciones del Ministerio del Poder Popular de Infraestructura y Vivienda',
            fecha_llegada=date(2026, 3, 22),
            conformidad_recepcion=True
        )
        
        inm_types = [
            ('Oficina de Registro', 'Nivel comercial con divisiones administrativas y bóveda'),
            ('Sede Judicial Local', 'Edificación judicial de 2 plantas con despachos y salas'),
            ('Galpón de Archivo Central', 'Depósito techado de alta capacidad con racks metálicos'),
            ('Terreno de Resguardo', 'Terreno cercado para custodia y almacenamiento al aire libre')
        ]
        
        for i in range(1, 51):
            itype, idesc = random.choice(inm_types)
            catastro = f"FICH-CAT-{4000 + i}"
            registro = f"TOMO-{i:02d}-FOLIO-{i+10:02d}-S{i}"
            codigo = f"DEM-INM-{3000 + i}"
            serial_fab = f"REGISTRO-INMUEBLE-{3000 + i}"
            
            rand_val = random.random()
            estado = 'ACTIVO' if rand_val < 0.85 else ('INACTIVO' if rand_val < 0.98 else 'DESINCORPORADO')
            
            valor = Decimal(f"{random.randint(85000, 650000)}.00")
            bcv = Decimal("36.50")
            valor_bs = valor * bcv

            inm = Inmueble.objects.create(
                nombre=f"{itype} - Código Catastral {i}",
                descripcion=f"{idesc}. Dirección regional judicial.",
                serial_fabrica=serial_fab,
                codigo_inventario=codigo,
                estado=estado,
                sede=sede_regional,
                orden_compra=oc_inm,
                valor_adquisicion=valor,
                tasa_bcv_compra=bcv,
                valor_adquisicion_bs=valor_bs,
                direccion_completa=f"Calle {i+1} entre avenidas {i+2} y {i+3}, Edificio DEM Nro {i}, Sector Judicial, Estado Miranda.",
                registro_propiedad=registro,
                area_terreno=Decimal(f"{random.randint(150, 1500)}.00"),
                area_construccion=Decimal(f"{random.randint(100, 1200)}.00"),
                catastro=catastro
            )

            TrazabilidadMovimientos.objects.create(
                bien=inm,
                tipo_movimiento='INCORPORACION',
                sede_destino=sede_regional,
                area_destino=area_admin,
                usuario_destino=u_operador,
                motivo='Incorporación en catastro catastral del bien inmueble institucional.',
                usuario_responsable=u_admin
            )

            if estado == 'ACTIVO':
                u_target = random.choice([u_admin, u_auditor, u_operador])
                Asignacion.objects.create(
                    bien=inm,
                    usuario=u_target,
                    area=area_admin,
                    activa=True
                )
                
                TrazabilidadMovimientos.objects.create(
                    bien=inm,
                    tipo_movimiento='ASIGNACION',
                    sede_origen=sede_regional,
                    sede_destino=sede_regional,
                    area_origen=area_admin,
                    area_destino=area_admin,
                    usuario_destino=u_target,
                    motivo=f'Custodia y resguardo administrativo asignada formalmente al funcionario @{u_target.username}.',
                    usuario_responsable=u_admin
                )

        self.stdout.write(self.style.SUCCESS("----------------------------------------------------------------------"))
        self.stdout.write(self.style.SUCCESS("¡LOTE MASIVO GENERADO EXITOSAMENTE AL 100%!"))
        self.stdout.write(self.style.SUCCESS(f"Total Bienes Informáticos creados: 50  (Orden: {oc_it.numero_orden})"))
        self.stdout.write(self.style.SUCCESS(f"Total Automotores creados:         50  (Orden: {oc_veh.numero_orden})"))
        self.stdout.write(self.style.SUCCESS(f"Total Inmuebles creados:           50  (Orden: {oc_inm.numero_orden})"))
        self.stdout.write(self.style.SUCCESS("Todos los bienes tienen sus correspondientes etiquetas y asignaciones."))
        self.stdout.write(self.style.SUCCESS("----------------------------------------------------------------------"))
