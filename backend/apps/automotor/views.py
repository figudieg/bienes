from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, BasePermission
from .models import Automotor
from .serializers import AutomotorSerializer

class IsAdminOrReadWrite(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method == 'DELETE':
            return getattr(request.user, 'rol', None) == 'ADMINISTRADOR'
        return True

class AutomotorViewSet(viewsets.ModelViewSet):
    queryset = Automotor.objects.all().order_by('-id')
    serializer_class = AutomotorSerializer
    permission_classes = [IsAdminOrReadWrite]
