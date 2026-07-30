from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BienesPublicosViewSet

router = DefaultRouter()
router.register(r'', BienesPublicosViewSet, basename='bienes')

urlpatterns = [
    path('', include(router.urls)),
]
