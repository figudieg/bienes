from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.forms.models import model_to_dict
from apps.auditoria.models import LogBien
from .models import Bien, Asignacion, TrazabilidadMovimientos
from decimal import Decimal

@receiver(pre_save, sender=Bien)
def capturar_estado_anterior(sender, instance, **kwargs):
    """
    Antes de guardar, capturamos el estado previo del bien para comparar 
    cambios de sede o estatus y calcular el valor en bolívares (Bs) según tasa BCV.
    """
    if instance.pk:
        try:
            instance._estado_previo = Bien.objects.get(pk=instance.pk)
        except Bien.DoesNotExist:
            instance._estado_previo = None
    else:
        instance._estado_previo = None

    # Calcular valor en Bs usando el scraping oficial del BCV si hay un valor de adquisición
    if instance.valor_adquisicion and instance.valor_adquisicion > 0:
        try:
            from core.bcv_service import get_tasa_bcv
            tasa = get_tasa_bcv()
            instance.tasa_bcv_compra = tasa
            instance.valor_adquisicion_bs = (instance.valor_adquisicion * tasa).quantize(Decimal('0.01'))
        except Exception as e:
            print(f"Error al obtener tasa BCV: {e}. Usando tasa por defecto.")
            # Fallback a la tasa por defecto guardada en el modelo
            instance.valor_adquisicion_bs = (instance.valor_adquisicion * instance.tasa_bcv_compra).quantize(Decimal('0.01'))

@receiver(post_save, sender=Bien)
def registrar_trazabilidad_bien(sender, instance, created, **kwargs):
    """
    Registra el movimiento del bien ante una incorporación, reubicación o desincorporación.
    """
    if created:
        # 1. Movimiento de Incorporación Inicial
        TrazabilidadMovimientos.objects.create(
            bien=instance,
            tipo_movimiento='INCORPORACION',
            sede_destino=instance.sede,
            motivo="Incorporación inicial de bien público en el inventario.",
            usuario_responsable=getattr(instance, '_creado_por', None)
        )
    else:
        # 2. Movimientos de Modificación (Reubicación de Sede o Desincorporación)
        prev = getattr(instance, '_estado_previo', None)
        if prev:
            # Detectar si cambió de Sede o de Estado
            if prev.sede != instance.sede:
                TrazabilidadMovimientos.objects.create(
                    bien=instance,
                    tipo_movimiento='REASIGNACION',
                    sede_origen=prev.sede,
                    sede_destino=instance.sede,
                    motivo=f"Reubicación de sede de {prev.sede.nombre} a {instance.sede.nombre}.",
                    usuario_responsable=getattr(instance, '_creado_por', None)
                )
            
            if prev.estado != instance.estado:
                tipo = 'DESINCORPORACION' if instance.estado == 'DESINCORPORADO' else 'REASIGNACION'
                motivo = f"Cambio de estado físico de {prev.estado} a {instance.estado}."
                if instance.estado == 'DESINCORPORADO':
                    motivo = "Desincorporación formal del bien público de los registros institucionales."
                
                TrazabilidadMovimientos.objects.create(
                    bien=instance,
                    tipo_movimiento=tipo,
                    sede_origen=prev.sede if tipo == 'DESINCORPORACION' else None,
                    motivo=motivo,
                    usuario_responsable=getattr(instance, '_creado_por', None)
                )

@receiver(post_save, sender=Asignacion)
def registrar_trazabilidad_asignacion(sender, instance, created, **kwargs):
    """
    Registra trazas ante asignaciones o reasignaciones de bienes a personal de la institución.
    """
    if created:
        bien = instance.bien
        # Si ya tiene una asignación previa, desactivamos las anteriores
        Asignacion.objects.filter(bien=bien, activa=True).exclude(pk=instance.pk).update(activa=False)
        
        # Registrar traza de Asignación/Reasignación
        TrazabilidadMovimientos.objects.create(
            bien=bien,
            tipo_movimiento='ASIGNACION',
            sede_destino=bien.sede,
            area_destino=instance.area,
            usuario_destino=instance.usuario,
            motivo=f"Asignación de bien público al operador {instance.usuario.get_full_name() or instance.usuario.username} en el área {instance.area.nombre}.",
            usuario_responsable=getattr(instance, '_creado_por', None)
        )