from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
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