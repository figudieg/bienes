from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InmuebleViewSet

router = DefaultRouter()
router.register(r'', InmuebleViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
