#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# Fix: psycopg2 en Windows con PostgreSQL en español falla al decodificar
# mensajes de error en Latin-1. Forzamos UTF-8 antes de cualquier conexión.
os.environ['PGCLIENTENCODING'] = 'utf8'
os.environ['PYTHONIOENCODING'] = 'utf-8'


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
