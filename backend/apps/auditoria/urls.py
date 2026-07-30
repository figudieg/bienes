from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LogBienViewSet, LogAccesoViewSet

router = DefaultRouter()
router.register(r'logs', LogBienViewSet, basename='auditoria-logs')
router.register(r'accesos', LogAccesoViewSet, basename='auditoria-accesos')

urlpatterns = [
    path('', include(router.urls)),
]