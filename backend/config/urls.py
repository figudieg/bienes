from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('apps.users.urls')),
    path('api/inventario/', include('apps.inventario.urls')),
    path('api/auditoria/', include('apps.auditoria.urls')),
    path('api/automotor/', include('apps.automotor.urls')),
    path('api/inmuebles/', include('apps.inmuebles.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)