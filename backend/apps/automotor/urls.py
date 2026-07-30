from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AutomotorViewSet

router = DefaultRouter()
router.register(r'', AutomotorViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
