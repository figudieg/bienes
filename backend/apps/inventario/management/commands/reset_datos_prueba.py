from django.core.management.base import BaseCommand

from apps.inventario.models import (
    Asignacion, TrazabilidadMovimientos, MantenimientoBien, Bien, Funcionario, OrdenCompra
)
from apps.auditoria.models import LogBien


class Command(BaseCommand):
    help = (
        "Limpia los datos de prueba (bienes, automotores, inmuebles, asignaciones, "
        "funcionarios, trazabilidad, mantenimientos y órdenes de compra) para dejar "
        "el sistema listo para probar el flujo desde cero. NO toca las cuentas de "
        "usuario (login) ni el directorio de Sedes/Áreas ya cargado."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--yes', action='store_true',
            help='Confirma la limpieza sin pedir confirmación interactiva.'
        )

    def handle(self, *args, **options):
        if not options['yes']:
            respuesta = input(
                "Esto borrará TODOS los bienes, automotores, inmuebles, asignaciones, "
                "funcionarios, trazabilidad, mantenimientos y órdenes de compra.\n"
                "Las cuentas de usuario y el directorio de Sedes/Áreas NO se tocan.\n"
                "¿Continuar? [s/N]: "
            )
            if respuesta.strip().lower() not in ('s', 'si', 'sí', 'y', 'yes'):
                self.stdout.write(self.style.WARNING("Cancelado."))
                return

        n_logs, _ = LogBien.objects.all().delete()
        n_asig, _ = Asignacion.objects.all().delete()
        n_traza, _ = TrazabilidadMovimientos.objects.all().delete()
        n_mant, _ = MantenimientoBien.objects.all().delete()
        n_bien, _ = Bien.objects.all().delete()  # cascada a Automotor/Inmueble
        n_func, _ = Funcionario.objects.all().delete()
        n_oc, _ = OrdenCompra.objects.all().delete()

        self.stdout.write(self.style.SUCCESS(
            "Limpieza completada:\n"
            f"  Logs de bienes: {n_logs}\n"
            f"  Asignaciones: {n_asig}\n"
            f"  Trazabilidad: {n_traza}\n"
            f"  Mantenimientos: {n_mant}\n"
            f"  Bienes (incl. automotores/inmuebles): {n_bien}\n"
            f"  Funcionarios: {n_func}\n"
            f"  Órdenes de compra: {n_oc}\n"
            "Se preservaron: cuentas de usuario, Sedes y Áreas."
        ))
