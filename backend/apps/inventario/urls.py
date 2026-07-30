from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SedeViewSet, 
    AreaViewSet, 
    OrdenCompraViewSet,
    BienViewSet,
    AsignacionViewSet,
    TrazabilidadViewSet,
    MantenimientoBienViewSet
)

router = DefaultRouter()
router.register(r'sedes', SedeViewSet, basename='sedes')
router.register(r'areas', AreaViewSet, basename='areas')
router.register(r'ordenes', OrdenCompraViewSet, basename='ordenes')
router.register(r'bienes', BienViewSet, basename='bienes')
router.register(r'asignaciones', AsignacionViewSet, basename='asignaciones')
router.register(r'trazabilidad', TrazabilidadViewSet, basename='trazabilidad')
router.register(r'mantenimientos', MantenimientoBienViewSet, basename='mantenimientos')

urlpatterns = [
    path('', include(router.urls)),
]