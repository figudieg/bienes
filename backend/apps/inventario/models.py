from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal

# Vida útil estimada (años) por categoría de bien mueble, para el cálculo de
# depreciación en línea recta. Automotores e inmuebles usan su propia vida útil
# fija (ver Bien.get_vida_util_anios) en vez de esta tabla.
VIDA_UTIL_POR_CATEGORIA = {
    'COMPUTADORA': 3,
    'PANTALLA': 3,
    'PERIFERICO': 3,
    'MOBILIARIO': 10,
    'EQUIPO_OFICINA': 10,
    'ELECTRODOMESTICO': 5,
    'HERRAMIENTA': 5,
    'OTRO': 10,
}
VIDA_UTIL_AUTOMOTOR = 5
VIDA_UTIL_INMUEBLE = 20

class Sede(models.Model):
    nombre = models.CharField(max_length=100)
    
    class Meta:
        verbose_name = 'Sede'
        verbose_name_plural = 'Sedes'

    def __str__(self):
        return self.nombre

class Area(models.Model):
    nombre = models.CharField(max_length=150)
    sede = models.ForeignKey(Sede, on_delete=models.PROTECT)
    codigo = models.CharField(max_length=20, blank=True, null=True, unique=True,
                               verbose_name="Código interno (Convalidación de Oficinas)")
    direccion_general = models.CharField(max_length=150, blank=True, null=True,
                                          verbose_name="Dirección/Unidad General a la que pertenece")
    activa = models.BooleanField(default=True, verbose_name="¿Oficina activa?")

    class Meta:
        verbose_name = 'Área'
        verbose_name_plural = 'Áreas'

    def __str__(self):
        return f"{self.nombre} - {self.sede.nombre}"

class Funcionario(models.Model):
    cedula = models.CharField(max_length=20, unique=True, verbose_name="Cédula de Identidad")
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100, blank=True, null=True)
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Funcionario'
        verbose_name_plural = 'Funcionarios'

    def __str__(self):
        return f"{self.cedula} - {self.nombres} {self.apellidos}"

    def get_full_name(self):
        return f"{self.nombres} {self.apellidos}"

class OrdenCompra(models.Model):
    """
    Registro de una orden de compra ya emitida por otra dependencia; la
    Dirección de Bienes Públicos no la origina, solo la carga como soporte
    (constancia) para poder asociarle los bienes incorporados.
    """
    numero_orden = models.CharField(max_length=50, unique=True)
    proveedor = models.CharField(max_length=150, default='Dirección Ejecutiva de la Magistratura (DEM)', verbose_name="Proveedor o Ente Donante")
    fecha_llegada = models.DateField()
    conformidad_recepcion = models.BooleanField(default=False)
    archivo_documento = models.FileField(upload_to='ordenes_compra/', verbose_name="Documento de la Orden de Compra (soporte)")

    class Meta:
        verbose_name = 'Orden de Compra'
        verbose_name_plural = 'Órdenes de Compra'

    def __str__(self):
        return self.numero_orden

class Bien(models.Model):
    ESTADOS = (
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('DESINCORPORADO', 'Desincorporado'),
    )
    CATEGORIAS = (
        ('COMPUTADORA', 'Computadora / Equipo de Computación'),
        ('PANTALLA', 'Pantalla / Monitor'),
        ('PERIFERICO', 'Periférico (Mouse, Teclado, etc.)'),
        ('MOBILIARIO', 'Mobiliario (Escritorio, Silla, Archivador)'),
        ('EQUIPO_OFICINA', 'Equipo de Oficina (Impresora, Fotocopiadora)'),
        ('ELECTRODOMESTICO', 'Electrodoméstico'),
        ('HERRAMIENTA', 'Herramienta / Equipo Técnico'),
        ('OTRO', 'Otro'),
    )
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    serial_fabrica = models.CharField(max_length=100, unique=True, null=True, blank=True)
    codigo_inventario = models.CharField(max_length=50, unique=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='ACTIVO')
    categoria = models.CharField(max_length=30, choices=CATEGORIAS, blank=True, null=True,
                                  verbose_name="Categoría del Bien Mueble")
    sede = models.ForeignKey(Sede, on_delete=models.PROTECT)
    orden_compra = models.ForeignKey(OrdenCompra, on_delete=models.PROTECT, null=True, blank=True, related_name='bienes')

    # Campos de clasificación física, para el formato oficial "Inventario de Bienes Muebles"
    caracteristicas = models.CharField(max_length=200, blank=True, null=True, verbose_name="Características")
    color_mueble = models.CharField(max_length=50, blank=True, null=True, verbose_name="Color")
    material = models.CharField(max_length=50, blank=True, null=True, verbose_name="Material")

    # Componente adicional (ej: monitor de un CPU, accesorio con serial propio)
    componente = models.CharField(max_length=100, blank=True, null=True, verbose_name="Componente")
    marca_componente = models.CharField(max_length=100, blank=True, null=True, verbose_name="Marca del Componente")
    modelo_componente = models.CharField(max_length=100, blank=True, null=True, verbose_name="Modelo del Componente")
    serial_componente = models.CharField(max_length=100, blank=True, null=True, verbose_name="Serial del Componente")

    # Nuevos campos para cumplimiento de valores en USD y Bs
    valor_adquisicion = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Valor de Adquisición ($)")
    tasa_bcv_compra = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('1.0000'), verbose_name="Tasa BCV de Compra")
    fecha_adquisicion = models.DateField(null=True, blank=True, verbose_name="Fecha de Adquisición")
    valor_adquisicion_bs = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Valor de Adquisición (Bs)")

    class Meta:
        verbose_name = 'Bien'
        verbose_name_plural = 'Bienes'

    def __str__(self):
        return f"{self.codigo_inventario} - {self.nombre}"

    def get_vida_util_anios(self):
        """Años de vida útil estimada, según el tipo real del bien (MTI)."""
        if hasattr(self, 'automotor'):
            return VIDA_UTIL_AUTOMOTOR
        if hasattr(self, 'inmueble'):
            return VIDA_UTIL_INMUEBLE
        return VIDA_UTIL_POR_CATEGORIA.get(self.categoria, 10)

    def get_depreciacion(self):
        """
        Depreciación en línea recta a partir de la fecha real de adquisición.
        Sin fecha de adquisición registrada no se puede calcular con certeza,
        así que se devuelve en cero en vez de inventar un valor.
        """
        vida_util = self.get_vida_util_anios()
        valor = float(self.valor_adquisicion or 0)

        if not self.fecha_adquisicion or valor <= 0:
            return {
                'vida_util_anios': vida_util,
                'anos_transcurridos': 0,
                'depreciacion_anual': 0.0,
                'depreciacion_acumulada': 0.0,
                'valor_neto': round(valor, 2),
                'porcentaje_depreciado': 0.0,
                'totalmente_depreciado': False,
            }

        dias_transcurridos = (timezone.localdate() - self.fecha_adquisicion).days
        anos_transcurridos = max(0.0, dias_transcurridos / 365.25)
        depreciacion_anual = valor / vida_util
        depreciacion_acumulada = min(depreciacion_anual * anos_transcurridos, valor)
        valor_neto = valor - depreciacion_acumulada

        return {
            'vida_util_anios': vida_util,
            'anos_transcurridos': round(anos_transcurridos, 1),
            'depreciacion_anual': round(depreciacion_anual, 2),
            'depreciacion_acumulada': round(depreciacion_acumulada, 2),
            'valor_neto': round(valor_neto, 2),
            'porcentaje_depreciado': round((depreciacion_acumulada / valor) * 100, 1),
            'totalmente_depreciado': depreciacion_acumulada >= valor,
        }

class Asignacion(models.Model):
    bien = models.ForeignKey(Bien, on_delete=models.PROTECT, related_name='asignaciones')
    funcionario = models.ForeignKey(Funcionario, on_delete=models.PROTECT, related_name='asignaciones', null=True)
    area = models.ForeignKey(Area, on_delete=models.PROTECT)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Asignación'
        verbose_name_plural = 'Asignaciones'

    def __str__(self):
        nombre_func = self.funcionario.nombres if self.funcionario else 'Sin asignar'
        return f"{self.bien.codigo_inventario} asignado a {nombre_func}"

class TrazabilidadMovimientos(models.Model):
    MOVIMIENTOS = (
        ('INCORPORACION', 'Incorporación'),
        ('ASIGNACION', 'Asignación'),
        ('REASIGNACION', 'Reasignación'),
        ('DESINCORPORACION', 'Desincorporación'),
    )
    bien = models.ForeignKey(Bien, on_delete=models.CASCADE, related_name='trazas')
    tipo_movimiento = models.CharField(max_length=30, choices=MOVIMIENTOS)
    sede_origen = models.ForeignKey(Sede, on_delete=models.SET_NULL, null=True, blank=True, related_name='trazas_origen')
    sede_destino = models.ForeignKey(Sede, on_delete=models.SET_NULL, null=True, blank=True, related_name='trazas_destino')
    area_origen = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True, related_name='trazas_area_origen')
    area_destino = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True, related_name='trazas_area_destino')
    funcionario_origen = models.ForeignKey(Funcionario, on_delete=models.SET_NULL, null=True, blank=True, related_name='trazas_funcionario_origen')
    funcionario_destino = models.ForeignKey(Funcionario, on_delete=models.SET_NULL, null=True, blank=True, related_name='trazas_funcionario_destino')
    fecha = models.DateTimeField(auto_now_add=True)
    motivo = models.TextField(blank=True, null=True)
    usuario_responsable = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='trazas_responsables')

    class Meta:
        verbose_name = 'Trazabilidad de Movimiento'
        verbose_name_plural = 'Trazabilidades de Movimientos'

    def __str__(self):
        return f"{self.tipo_movimiento} - {self.bien.codigo_inventario} - {self.fecha.strftime('%d/%m/%Y')}"

class MantenimientoBien(models.Model):
    TIPOS = (
        ('PREVENTIVO', 'Preventivo'),
        ('CORRECTIVO', 'Correctivo'),
    )
    bien = models.ForeignKey(Bien, on_delete=models.CASCADE, related_name='mantenimientos')
    numero_ficha = models.CharField(max_length=50, verbose_name="Número de Ficha/Reporte")
    fecha_ficha = models.DateField(verbose_name="Fecha de la Ficha")
    tipo_mantenimiento = models.CharField(max_length=20, choices=TIPOS, default='CORRECTIVO')
    actividad_realizada = models.TextField(verbose_name="Actividad Realizada")
    materiales_empleados = models.TextField(verbose_name="Materiales Empleados", blank=True, null=True)
    numero_factura = models.CharField(max_length=100, default="Autogestión", verbose_name="Número de Factura")
    costo = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Costo (Bs/$)")
    fecha_mantenimiento = models.DateField(verbose_name="Fecha del Mantenimiento")
    nota = models.TextField(blank=True, null=True, verbose_name="Notas/Observaciones")
    
    # Firmas/Responsables
    reparado_por = models.CharField(max_length=150, verbose_name="Reparado por")
    conformado_por = models.CharField(max_length=150, verbose_name="Conformado por")
    responsable_administrativo = models.CharField(max_length=150, verbose_name="Responsable Administrativo")

    class Meta:
        verbose_name = 'Mantenimiento de Bien'
        verbose_name_plural = 'Mantenimientos de Bienes'

    def __str__(self):
        return f"Mantenimiento {self.numero_ficha} - {self.bien.codigo_inventario}"