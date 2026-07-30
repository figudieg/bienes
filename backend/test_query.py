import os
import django
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
settings.ALLOWED_HOSTS = ['*']

from rest_framework.test import APIClient
from apps.users.models import CustomUser

try:
    user = CustomUser.objects.get(username='operador')
    client = APIClient()
    client.force_authenticate(user=user)
    
    print("Iniciando consulta de bienes...")
    t0 = time.time()
    res = client.get('/api/inventario/bienes/')
    t1 = time.time()
    
    print('Status Code:', res.status_code)
    print('Time elapsed:', t1 - t0, 'seconds')
    
    if res.status_code == 200:
        print('Bienes count:', len(res.data))
    else:
        print('Error Response status:', res.status_code)
except Exception as e:
    import traceback
    traceback.print_exc()
