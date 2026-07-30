from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, BasePermission
from .models import Inmueble
from .serializers import InmuebleSerializer

class IsAdminOrReadWrite(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method == 'DELETE':
            return getattr(request.user, 'rol', None) == 'ADMINISTRADOR'
        return True

class InmuebleViewSet(viewsets.ModelViewSet):
    queryset = Inmueble.objects.all().order_by('-id')
    serializer_class = InmuebleSerializer
    permission_classes = [IsAdminOrReadWrite]
