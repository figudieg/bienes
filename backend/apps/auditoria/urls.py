from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LogBienViewSet, LogAccesoViewSet, HallazgoViewSet

router = DefaultRouter()
router.register(r'logs', LogBienViewSet, basename='auditoria-logs')
router.register(r'accesos', LogAccesoViewSet, basename='auditoria-accesos')
router.register(r'hallazgos', HallazgoViewSet, basename='auditoria-hallazgos')

urlpatterns = [
    path('', include(router.urls)),
]