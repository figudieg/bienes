from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission, SAFE_METHODS
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from django.db.models import Prefetch
from .models import Sede, Area, OrdenCompra, Bien, Asignacion, Funcionario
from .serializers import (
    SedeSerializer, AreaSerializer, OrdenCompraSerializer,
    BienSerializer, AsignacionSerializer, FuncionarioSerializer
)

class IsAdminOrReadWrite(BasePermission):
    """Permite DELETE solo a ADMINISTRADOR. Lectura y escritura a cualquier autenticado."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method == 'DELETE':
            return getattr(request.user, 'rol', None) == 'ADMINISTRADOR'
        return True

class SedeViewSet(viewsets.ModelViewSet):
    queryset = Sede.objects.all().order_by('nombre')
    serializer_class = SedeSerializer
    permission_classes = [IsAdminOrReadWrite]

class AreaViewSet(viewsets.ModelViewSet):
    queryset = Area.objects.all().order_by('nombre')
    serializer_class = AreaSerializer
    permission_classes = [IsAdminOrReadWrite]

class FuncionarioViewSet(viewsets.ModelViewSet):
    queryset = Funcionario.objects.all().order_by('nombres', 'apellidos')
    serializer_class = FuncionarioSerializer
    permission_classes = [IsAdminOrReadWrite]

    @action(detail=False, methods=['get'], url_path='buscar-por-cedula')
    def buscar_por_cedula(self, request):
        """
        Busca un funcionario ya registrado localmente por cédula (sin consultar
        SISCOM). Sirve como respaldo cuando no hay acceso a la red del DEM, para
        poder seguir viendo el perfil de funcionarios ya conocidos por el sistema.
        Uso: GET /api/inventario/funcionarios/buscar-por-cedula/?cedula=12345678
        """
        from django.db.models import Q

        cedula = request.query_params.get('cedula', '').strip()
        if not cedula:
            return Response({'error': 'Debe proporcionar un número de cédula.'}, status=400)

        funcionario = Funcionario.objects.select_related('area').filter(
            Q(cedula=cedula) | Q(cedula=f"V-{cedula}") | Q(cedula=f"E-{cedula}")
        ).first()
        if not funcionario:
            return Response({'error': f'No se encontró un funcionario registrado con la cédula {cedula}.'}, status=404)

        return Response(FuncionarioSerializer(funcionario).data)

    @action(detail=True, methods=['get'], url_path='perfil')
    def perfil(self, request, pk=None):
        funcionario = self.get_object()
        asignaciones = Asignacion.objects.filter(funcionario=funcionario, activa=True).select_related(
            'bien', 'area', 'bien__sede'
        ).order_by('-fecha_asignacion')

        bienes_data = []
        for a in asignaciones:
            b = a.bien
            if hasattr(b, 'automotor'):
                tipo = 'Automotor'
            elif hasattr(b, 'inmueble'):
                tipo = 'Inmueble'
            else:
                tipo = 'Bien Mueble'
            bienes_data.append({
                'asignacion_id': a.id,
                'bien_id': b.id,
                'codigo_inventario': b.codigo_inventario,
                'nombre': b.nombre,
                'tipo': tipo,
                'estado': b.estado,
                'sede_nombre': b.sede.nombre if b.sede else None,
                'area_nombre': a.area.nombre if a.area else None,
                'fecha_asignacion': a.fecha_asignacion,
            })

        return Response({
            'funcionario': FuncionarioSerializer(funcionario).data,
            'total_bienes': len(bienes_data),
            'bienes': bienes_data,
        })

class OrdenCompraViewSet(viewsets.ModelViewSet):
    queryset = OrdenCompra.objects.all().order_by('-fecha_llegada')
    serializer_class = OrdenCompraSerializer
    permission_classes = [IsAdminOrReadWrite]

    @action(detail=True, methods=['get'], url_path='reporte-pdf')
    def reporte_pdf(self, request, pk=None):
        """Genera un reporte PDF de la orden de compra y sus bienes asociados."""
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        import io

        orden = self.get_object()
        bienes = orden.bienes.all()

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph(f"Reporte de Orden de Compra: {orden.numero_orden}", styles['Title']))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"Fecha de Llegada: {orden.fecha_llegada}", styles['Normal']))
        elements.append(Paragraph(f"Conformidad: {'Sí' if orden.conformidad_recepcion else 'Pendiente'}", styles['Normal']))
        elements.append(Spacer(1, 20))

        if bienes.exists():
            elements.append(Paragraph("Bienes Asociados:", styles['Heading2']))
            data = [['Código', 'Nombre', 'Serial', 'Estado', 'Sede']]
            for b in bienes:
                data.append([b.codigo_inventario, b.nombre, b.serial_fabrica or '—', b.estado, b.sede.nombre])
            
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
            ]))
            elements.append(table)
        else:
            elements.append(Paragraph("Sin bienes asociados a esta orden.", styles['Normal']))

        doc.build(elements)
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Reporte_Orden_{orden.numero_orden}.pdf"'
        return response

class BienViewSet(viewsets.ModelViewSet):
    queryset = Bien.objects.select_related('sede', 'orden_compra', 'automotor', 'inmueble').prefetch_related(
        Prefetch(
            'asignaciones',
            queryset=Asignacion.objects.filter(activa=True).select_related('funcionario', 'area'),
            to_attr='asignaciones_activas',
        )
    ).all().order_by('-id')
    serializer_class = BienSerializer
    permission_classes = [IsAdminOrReadWrite]

    @action(detail=False, methods=['get'], url_path='db-status', permission_classes=[AllowAny])
    def db_status(self, request):
        from django.conf import settings
        db_engine = settings.DATABASES['default']['ENGINE']
        engine_type = 'sqlite' if 'sqlite' in db_engine else 'postgresql'
        return Response({'status': 'ok', 'engine': engine_type})

    def _reasignar_bien(self, bien, sede_destino, area_destino, funcionario_destino, motivo, usuario):
        from .models import TrazabilidadMovimientos, Asignacion

        sede_origen = bien.sede
        asignacion_activa = bien.asignaciones.filter(activa=True).first()
        area_origen = asignacion_activa.area if asignacion_activa else None
        funcionario_origen = asignacion_activa.funcionario if asignacion_activa else None

        if asignacion_activa:
            asignacion_activa.activa = False
            asignacion_activa.save()

        bien.sede = sede_destino
        bien.estado = 'ACTIVO'
        bien.save()

        if funcionario_destino:
            Asignacion.objects.create(
                bien=bien,
                funcionario=funcionario_destino,
                area=area_destino,
                activa=True
            )

        return TrazabilidadMovimientos.objects.create(
            bien=bien,
            tipo_movimiento='REASIGNACION',
            sede_origen=sede_origen,
            sede_destino=sede_destino,
            area_origen=area_origen,
            area_destino=area_destino,
            funcionario_origen=funcionario_origen,
            funcionario_destino=funcionario_destino,
            motivo=motivo,
            usuario_responsable=usuario
        )

    def _desincorporar_bien(self, bien, motivo, usuario):
        from .models import TrazabilidadMovimientos
        from rest_framework.exceptions import ValidationError

        if bien.estado == 'DESINCORPORADO':
            raise ValidationError(
                f'El bien "{bien.codigo_inventario}" ya está desincorporado.'
            )

        sede_origen = bien.sede
        asignacion_activa = bien.asignaciones.filter(activa=True).first()
        area_origen = asignacion_activa.area if asignacion_activa else None
        funcionario_origen = asignacion_activa.funcionario if asignacion_activa else None

        if asignacion_activa:
            asignacion_activa.activa = False
            asignacion_activa.save()

        bien.estado = 'DESINCORPORADO'
        bien.save()

        return TrazabilidadMovimientos.objects.create(
            bien=bien,
            tipo_movimiento='DESINCORPORACION',
            sede_origen=sede_origen,
            area_origen=area_origen,
            funcionario_origen=funcionario_origen,
            motivo=motivo,
            usuario_responsable=usuario
        )

    @action(detail=True, methods=['post'], url_path='reasignar')
    def reasignar(self, request, pk=None):
        from django.db import transaction
        from django.shortcuts import get_object_or_404
        from .models import Sede, Area, Funcionario
        import io
        from .pdf_generator import generate_multi_reasignacion_pdf

        bien = self.get_object()
        sede_destino_id = request.data.get('sede_destino_id')
        area_destino_id = request.data.get('area_destino_id')
        funcionario_destino_id = request.data.get('funcionario_destino_id')
        motivo = request.data.get('motivo', 'Reasignación')
        cedente_nombre = request.data.get('cedente_nombre', 'N/A')
        receptor_nombre = request.data.get('receptor_nombre', 'N/A')

        sede_destino = get_object_or_404(Sede, id=sede_destino_id)
        area_destino = get_object_or_404(Area, id=area_destino_id)
        funcionario_destino = get_object_or_404(Funcionario, id=funcionario_destino_id) if funcionario_destino_id else None

        with transaction.atomic():
            traza = self._reasignar_bien(bien, sede_destino, area_destino, funcionario_destino, motivo, request.user)

        buffer = io.BytesIO()
        generate_multi_reasignacion_pdf(buffer, [traza], cedente_nombre, receptor_nombre)
        buffer.seek(0)

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Comprobante_Reasignacion_{bien.codigo_inventario}.pdf"'
        return response

    @action(detail=True, methods=['post'], url_path='desincorporar')
    def desincorporar(self, request, pk=None):
        from django.db import transaction
        import io
        from .pdf_generator import generate_multi_desincorporacion_pdf

        bien = self.get_object()
        motivo = request.data.get('motivo', 'Desincorporación')

        with transaction.atomic():
            traza = self._desincorporar_bien(bien, motivo, request.user)

        buffer = io.BytesIO()
        generate_multi_desincorporacion_pdf(buffer, [traza], motivo)
        buffer.seek(0)

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Comprobante_Desincorporacion_{bien.codigo_inventario}.pdf"'
        return response

    @action(detail=False, methods=['post'], url_path='reasignar-masivo')
    def reasignar_masivo(self, request):
        from django.db import transaction
        from django.shortcuts import get_object_or_404
        from .models import Sede, Area, Funcionario
        import io

        bien_ids = request.data.get('bien_ids', [])
        sede_destino_id = request.data.get('sede_destino_id')
        area_destino_id = request.data.get('area_destino_id')
        funcionario_destino_id = request.data.get('funcionario_destino_id')
        motivo = request.data.get('motivo', 'Reasignación masiva')
        cedente_nombre = request.data.get('cedente_nombre', 'N/A')
        receptor_nombre = request.data.get('receptor_nombre', 'N/A')

        if not bien_ids:
            return Response({'error': 'Debe seleccionar al menos un bien.'}, status=400)

        sede_destino = get_object_or_404(Sede, id=sede_destino_id)
        area_destino = get_object_or_404(Area, id=area_destino_id)
        funcionario_destino = get_object_or_404(Funcionario, id=funcionario_destino_id) if funcionario_destino_id else None

        trazas_creadas = []

        with transaction.atomic():
            for b_id in bien_ids:
                bien = get_object_or_404(Bien, id=b_id)
                traza = self._reasignar_bien(bien, sede_destino, area_destino, funcionario_destino, motivo, request.user)
                trazas_creadas.append(traza)

        # Generar PDF masivo
        buffer = io.BytesIO()
        from .pdf_generator import generate_multi_reasignacion_pdf
        generate_multi_reasignacion_pdf(buffer, trazas_creadas, cedente_nombre, receptor_nombre)
        buffer.seek(0)

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Comprobante_Reasignacion_Masiva.pdf"'
        return response

    @action(detail=False, methods=['post'], url_path='desincorporar-masivo')
    def desincorporar_masivo(self, request):
        from django.db import transaction
        from django.shortcuts import get_object_or_404
        import io
        from .pdf_generator import generate_multi_desincorporacion_pdf

        bien_ids = request.data.get('bien_ids', [])
        motivo = request.data.get('motivo', 'Desincorporación masiva')

        if not bien_ids:
            return Response({'error': 'Debe seleccionar al menos un bien.'}, status=400)

        trazas_creadas = []

        with transaction.atomic():
            for b_id in bien_ids:
                bien = get_object_or_404(Bien, id=b_id)
                traza = self._desincorporar_bien(bien, motivo, request.user)
                trazas_creadas.append(traza)

        # Generar PDF masivo
        buffer = io.BytesIO()
        generate_multi_desincorporacion_pdf(buffer, trazas_creadas, motivo)
        buffer.seek(0)

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Comprobante_Desincorporacion_Masiva.pdf"'
        return response

    @action(detail=False, methods=['post'], url_path='mantenimiento-masivo')
    def mantenimiento_masivo(self, request):
        from django.db import transaction
        from django.shortcuts import get_object_or_404
        from .models import MantenimientoBien
        import io
        from .pdf_generator import generate_multi_mantenimiento_pdf
        import datetime
        
        bien_ids = request.data.get('bien_ids', [])
        numero_ficha = request.data.get('numero_ficha', 'MANT-MASIVO')
        fecha_ficha_str = request.data.get('fecha_ficha', str(datetime.date.today()))
        tipo_mantenimiento = request.data.get('tipo_mantenimiento', 'CORRECTIVO')
        actividad_realizada = request.data.get('actividad_realizada', '')
        materiales_empleados = request.data.get('materiales_empleados', '')
        numero_factura = request.data.get('numero_factura', 'Autogestión')
        costo = request.data.get('costo', '0.00')
        fecha_mantenimiento_str = request.data.get('fecha_mantenimiento', str(datetime.date.today()))
        reparado_por = request.data.get('reparado_por', 'Soporte Técnico DEM')
        conformado_por = request.data.get('conformado_por', 'Jefe de Bienes DEM')
        responsable_administrativo = request.data.get('responsable_administrativo', 'Director DEM')
        nota = request.data.get('nota', '')
        
        if not bien_ids:
            return Response({'error': 'Debe seleccionar al menos un bien.'}, status=400)

        try:
            costo_val = float(costo)
            if costo_val < 0:
                return Response({'error': 'El costo del mantenimiento no puede ser negativo.'}, status=400)
        except (ValueError, TypeError):
            return Response({'error': 'El costo del mantenimiento debe ser un número válido.'}, status=400)
            
        mantenimientos_creados = []
        
        try:
            fecha_ficha = datetime.datetime.strptime(fecha_ficha_str, "%Y-%m-%d").date()
        except ValueError:
            fecha_ficha = datetime.date.today()
            
        try:
            fecha_mantenimiento = datetime.datetime.strptime(fecha_mantenimiento_str, "%Y-%m-%d").date()
        except ValueError:
            fecha_mantenimiento = datetime.date.today()
            
        with transaction.atomic():
            for b_id in bien_ids:
                bien = get_object_or_404(Bien, id=b_id)
                
                # Crear registro de mantenimiento
                mant = MantenimientoBien.objects.create(
                    bien=bien,
                    numero_ficha=numero_ficha,
                    fecha_ficha=fecha_ficha,
                    tipo_mantenimiento=tipo_mantenimiento,
                    actividad_realizada=actividad_realizada,
                    materiales_empleados=materiales_empleados,
                    numero_factura=numero_factura,
                    costo=costo,
                    fecha_mantenimiento=fecha_mantenimiento,
                    reparado_por=reparado_por,
                    conformado_por=conformado_por,
                    responsable_administrativo=responsable_administrativo,
                    nota=nota
                )
                mantenimientos_creados.append(mant)
                
        # Generar PDF masivo
        buffer = io.BytesIO()
        generate_multi_mantenimiento_pdf(buffer, mantenimientos_creados)
        buffer.seek(0)
        
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Ficha_Mantenimiento_Masiva_{numero_ficha}.pdf"'
        return response

    @action(detail=False, methods=['post'], url_path='importar-excel')
    def importar_excel(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': 'No se cargó ningún archivo.'}, status=400)
        
        import tempfile
        import os
        from .excel_parser import import_excel_file
        
        suffix = os.path.splitext(file_obj.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            for chunk in file_obj.chunks():
                temp_file.write(chunk)
            temp_path = temp_file.name

        try:
            result = import_excel_file(temp_path, file_obj.name)
            os.remove(temp_path)
            if result['status'] == 'error':
                return Response(result, status=400)
            return Response(result)
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return Response({'error': str(e)}, status=500)

    @action(detail=True, methods=['get'], url_path='comprobante-incorporacion-pdf')
    def comprobante_incorporacion_pdf(self, request, pk=None):
        import io
        from django.http import HttpResponse
        from .pdf_generator import generate_incorporacion_pdf

        bien = self.get_object()
        if not bien.orden_compra:
            return Response({'error': 'Este bien no posee una Orden de Compra/Incorporación asociada.'}, status=400)
            
        oc = bien.orden_compra
        bienes = oc.bienes.all()
        
        buffer = io.BytesIO()
        generate_incorporacion_pdf(buffer, oc, bienes)
        buffer.seek(0)
        
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Comprobante_Incorporacion_{oc.numero_orden}.pdf"'
        return response

    @action(detail=False, methods=['get'], url_path='inventario-general-pdf')
    def inventario_general_pdf(self, request):
        import io
        from django.db.models import Q
        from django.http import HttpResponse
        from .pdf_generator import generate_inventario_general_pdf

        bienes = self.get_queryset()

        sede_id = request.query_params.get('sede')
        area_id = request.query_params.get('area')
        direccion_general = request.query_params.get('direccion_general')
        estado = request.query_params.get('estado')
        tipo = request.query_params.get('tipo')
        search = request.query_params.get('search')

        if sede_id:
            bienes = bienes.filter(sede_id=sede_id)
        if estado:
            bienes = bienes.filter(estado=estado)
        if area_id:
            bienes = bienes.filter(asignaciones__activa=True, asignaciones__area_id=area_id)
        elif direccion_general:
            bienes = bienes.filter(asignaciones__activa=True, asignaciones__area__direccion_general=direccion_general)
        if search:
            bienes = bienes.filter(
                Q(nombre__icontains=search) | Q(codigo_inventario__icontains=search) | Q(serial_fabrica__icontains=search)
            )
        if tipo == 'AUTOMOTOR':
            bienes = bienes.filter(automotor__isnull=False)
        elif tipo == 'INMUEBLE':
            bienes = bienes.filter(inmueble__isnull=False)
        elif tipo == 'MUEBLE':
            bienes = bienes.filter(automotor__isnull=True, inmueble__isnull=True)

        bienes = bienes.distinct()

        buffer = io.BytesIO()
        generate_inventario_general_pdf(buffer, bienes)
        buffer.seek(0)

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Inventario_General_Bienes.pdf"'
        return response

class AsignacionViewSet(viewsets.ModelViewSet):
    queryset = Asignacion.objects.select_related('bien', 'funcionario', 'area').all().order_by('-fecha_asignacion')
    serializer_class = AsignacionSerializer
    permission_classes = [IsAdminOrReadWrite]

from .models import TrazabilidadMovimientos, MantenimientoBien
from .serializers import TrazabilidadSerializer, MantenimientoBienSerializer

class TrazabilidadViewSet(viewsets.ModelViewSet):
    queryset = TrazabilidadMovimientos.objects.select_related(
        'bien', 'sede_origen', 'sede_destino', 'area_origen', 'area_destino', 
        'funcionario_origen', 'funcionario_destino', 'usuario_responsable'
    ).all().order_by('-fecha')
    serializer_class = TrazabilidadSerializer
    permission_classes = [IsAdminOrReadWrite]

    @action(detail=True, methods=['get'], url_path='comprobante-reasignacion-pdf')
    def comprobante_reasignacion_pdf(self, request, pk=None):
        import io
        from django.http import HttpResponse
        from .pdf_generator import generate_reasignacion_pdf

        traza = self.get_object()
        if traza.tipo_movimiento != 'REASIGNACION':
            return Response({'error': 'Este movimiento no es una Reasignación.'}, status=400)
            
        buffer = io.BytesIO()
        generate_reasignacion_pdf(buffer, traza)
        buffer.seek(0)
        
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Comprobante_Reasignacion_{traza.id}.pdf"'
        return response

class MantenimientoBienViewSet(viewsets.ModelViewSet):
    queryset = MantenimientoBien.objects.select_related('bien').all().order_by('-fecha_mantenimiento')
    serializer_class = MantenimientoBienSerializer
    permission_classes = [IsAdminOrReadWrite]

    @action(detail=True, methods=['get'], url_path='reporte-pdf')
    def reporte_pdf(self, request, pk=None):
        import io
        from django.http import HttpResponse
        from .pdf_generator import generate_ficha_mantenimiento_pdf

        mant = self.get_object()
        buffer = io.BytesIO()
        generate_ficha_mantenimiento_pdf(buffer, mant)
        buffer.seek(0)
        
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Ficha_Mantenimiento_{mant.numero_ficha}.pdf"'
        return response
