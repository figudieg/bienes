import os
import re

import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.inventario.models import Area, Sede

DEFAULT_PATH = os.path.join(settings.BASE_DIR.parent, 'scripts', 'convalidacion_oficinas.xls')

CERRADO_RE = re.compile(r'\(\s*CERRAD[OA]\s*\)', re.IGNORECASE)


class Command(BaseCommand):
    help = (
        "Importa el directorio real de oficinas/dependencias del DEM desde el Excel de "
        "'Convalidación de Oficinas' y lo carga como registros de Area (con código, "
        "dirección general y estado activo/cerrado)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--file', dest='file', default=DEFAULT_PATH,
            help='Ruta al archivo .xls de convalidación de oficinas.'
        )
        parser.add_argument(
            '--sede', dest='sede', default='Sede Principal DEM',
            help='Nombre de la Sede a la que se asociarán las oficinas importadas.'
        )

    def handle(self, *args, **options):
        path = options['file']
        if not os.path.exists(path):
            raise CommandError(f"No se encontró el archivo: {path}")

        sede, _ = Sede.objects.get_or_create(nombre=options['sede'])

        xls = pd.ExcelFile(path)
        sheet_name = xls.sheet_names[0]
        df = xls.parse(sheet_name, header=None)

        direccion_general = None
        creadas, actualizadas, cerradas = 0, 0, 0

        for _, row in df.iterrows():
            col0, col1, col2 = row[0], row[1], row[2]

            codigo_valido = isinstance(col1, str) and col1.strip()
            nombre_valido = isinstance(col2, str) and col2.strip()

            if not codigo_valido and not nombre_valido:
                # Fila de encabezado de sección (ej. "03 - DIRECCIÓN GENERAL DE
                # ADMINISTRACIÓN Y FINANZAS") o fila vacía/pie de página.
                if isinstance(col0, str) and ' - ' in col0:
                    direccion_general = col0.split(' - ', 1)[1].strip()
                continue

            if not (codigo_valido and nombre_valido):
                # Fila incompleta (no debería ocurrir en un archivo bien formado).
                continue

            codigo = col1.strip()
            nombre_raw = col2.strip()
            activa = not CERRADO_RE.search(nombre_raw)
            nombre = CERRADO_RE.sub('', nombre_raw).strip()
            nombre = re.sub(r'\s{2,}', ' ', nombre)

            area, created = Area.objects.update_or_create(
                codigo=codigo,
                defaults={
                    'nombre': nombre,
                    'sede': sede,
                    'direccion_general': direccion_general,
                    'activa': activa,
                },
            )
            if created:
                creadas += 1
            else:
                actualizadas += 1
            if not activa:
                cerradas += 1

        self.stdout.write(self.style.SUCCESS(
            f"Oficinas importadas: {creadas} creadas, {actualizadas} actualizadas "
            f"({cerradas} marcadas como cerradas/inactivas)."
        ))
