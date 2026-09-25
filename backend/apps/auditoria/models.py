from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from apps.inventario.models import Bien
from apps.automotor.models import Automotor
from apps.inmuebles.models import Inmueble

class LogBien(models.Model):
    bien = models.ForeignKey(Bien, on_delete=models.CASCADE, related_name='logs')
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Usuario responsable (si está disponible en el contexto)"
    )
    accion = models.CharField(max_length=50)
    fecha = models.DateTimeField(auto_now_add=True)
    detalles = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Log de Bien'
        verbose_name_plural = 'Logs de Bienes'

    def __str__(self):
        return f"Log {self.bien.codigo_inventario} - {self.accion}"

# Signal simple para registrar la creación o modificación. Se registra para
# Bien y también para Automotor/Inmueble: al ser herencia multi-tabla, guardar
# una instancia de Automotor o Inmueble dispara post_save con sender=Automotor
# o sender=Inmueble (no sender=Bien), así que hay que escuchar los tres.
@receiver(post_save, sender=Bien)
@receiver(post_save, sender=Automotor)
@receiver(post_save, sender=Inmueble)
def registrar_auditoria_bien(sender, instance, created, **kwargs):
    accion = 'CREACION' if created else 'MODIFICACION'
    LogBien.objects.create(
        bien_id=instance.pk,
        accion=accion,
        detalles=f"El bien {instance.codigo_inventario} ha sido {'registrado' if created else 'modificado'} en el sistema."
    )

class Hallazgo(models.Model):
    """
    Observación de auditoría/fiscalización sobre un bien específico (ej: un
    levantamiento físico que no coincide, un daño no reportado, un serial que
    no corresponde). Alimenta el Informe de Auditoría y Fiscalización en PDF.
    """
    GRAVEDADES = (
        ('ALTA', 'Alta'),
        ('MEDIA', 'Media'),
        ('BAJA', 'Baja'),
    )
    ESTADOS = (
        ('PENDIENTE', 'Pendiente'),
        ('EN_PROCESO', 'En Proceso'),
        ('RESUELTO', 'Resuelto'),
    )
    bien = models.ForeignKey(Bien, on_delete=models.CASCADE, related_name='hallazgos')
    descripcion = models.TextField(verbose_name="Descripción del Hallazgo")
    gravedad = models.CharField(max_length=10, choices=GRAVEDADES, default='MEDIA')
    estado = models.CharField(max_length=15, choices=ESTADOS, default='PENDIENTE')
    fecha_deteccion = models.DateField(default=timezone.localdate, verbose_name="Fecha de Detección")
    reportado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='hallazgos_reportados'
    )
    fecha_resolucion = models.DateField(null=True, blank=True, verbose_name="Fecha de Resolución")
    resuelto_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='hallazgos_resueltos'
    )
    observaciones_resolucion = models.TextField(blank=True, null=True, verbose_name="Observaciones de Resolución")

    class Meta:
        verbose_name = 'Hallazgo de Auditoría'
        verbose_name_plural = 'Hallazgos de Auditoría'
        ordering = ['-fecha_deteccion', '-id']

    def __str__(self):
        return f"Hallazgo {self.bien.codigo_inventario} ({self.gravedad}) - {self.estado}"

class LogAcceso(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Usuario"
    )
    ip_address = models.GenericIPAddressField(verbose_name="Dirección IP", default="127.0.0.1")
    accion = models.CharField(max_length=100, default="INICIO_SESION", verbose_name="Acción Realizada")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora Exacta")
    detalles = models.TextField(blank=True, null=True, verbose_name="Detalles")

    class Meta:
        db_table = 'log_acceso'
        verbose_name = 'Log de Acceso y Seguridad'
        verbose_name_plural = 'Logs de Accesos y Seguridad'

    def __str__(self):
        nombre = self.usuario.username if self.usuario else "SISTEMA"
        return f"{nombre} - {self.accion} - {self.fecha.strftime('%d/%m/%Y %H:%M:%S')}"