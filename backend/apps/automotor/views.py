from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, BasePermission
from django.db.models import Prefetch
from apps.inventario.models import Asignacion
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
    queryset = Automotor.objects.prefetch_related(
        Prefetch(
            'asignaciones',
            queryset=Asignacion.objects.filter(activa=True).select_related('funcionario', 'area'),
            to_attr='asignaciones_activas',
        )
    ).all().order_by('-id')
    serializer_class = AutomotorSerializer
    permission_classes = [IsAdminOrReadWrite]
