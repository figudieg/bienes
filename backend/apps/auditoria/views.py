from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from django.utils import timezone
from .models import LogBien, LogAcceso, Hallazgo
from .serializers import LogBienSerializer, LogAccesoSerializer, HallazgoSerializer

class LogBienViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Vista de solo lectura para los logs de bienes.
    """
    queryset = LogBien.objects.all().order_by('-fecha')
    serializer_class = LogBienSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='reporte-pdf')
    def reporte_pdf(self, request):
        """Genera el Informe de Auditoría y Fiscalización, con los hallazgos reales registrados."""
        import io
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from apps.inventario.models import Bien
        from apps.inventario.pdf_generator import (
            build_pdf_header, build_signature_block, band_row, value_row, _styles,
            HEADER_BG, SUBHEADER_BG, BORDER_COLOR,
        )

        s = _styles()
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
        elements = []

        hoy = timezone.localdate()
        build_pdf_header(elements, "Informe de Auditoría y Fiscalización de Bienes Públicos",
                          f"AUD-{hoy.strftime('%Y%m%d')}", hoy.strftime("%d/%m/%Y"))

        # Resumen de inventario fiscalizado
        total_bienes = Bien.objects.count()
        activos = Bien.objects.filter(estado='ACTIVO').count()
        inactivos = Bien.objects.filter(estado='INACTIVO').count()
        desincorporados = Bien.objects.filter(estado='DESINCORPORADO').count()

        band_row(elements, ["TOTAL BIENES", "ACTIVOS", "INACTIVOS", "DESINCORPORADOS"],
                  widths=[1.875 * inch] * 4)
        value_row(elements, [total_bienes, activos, inactivos, desincorporados], widths=[1.875 * inch] * 4)
        elements.append(Spacer(1, 14))

        # Hallazgos de auditoría (el cuerpo real del informe)
        hallazgos = Hallazgo.objects.select_related('bien', 'reportado_por').order_by('-fecha_deteccion')[:200]
        elements.append(Paragraph("<b>Hallazgos de Auditoría y Fiscalización</b>", s['cell_bold']))
        elements.append(Spacer(1, 6))

        gravedad_hex = {'ALTA': '#c0392b', 'MEDIA': '#b8860b', 'BAJA': '#000000'}
        if hallazgos.exists():
            header = ["BIEN", "DESCRIPCIÓN", "GRAVEDAD", "ESTADO", "FECHA", "REPORTADO POR"]
            data = [[Paragraph(f"<b>{h}</b>", s['cell_bold']) for h in header]]
            for h in hallazgos:
                data.append([
                    Paragraph(f"<b>{h.bien.codigo_inventario}</b><br/>{h.bien.nombre}", s['cell']),
                    Paragraph(h.descripcion, s['cell']),
                    Paragraph(f"<font color='{gravedad_hex.get(h.gravedad, '#000000')}'><b>{h.get_gravedad_display()}</b></font>", s['cell']),
                    Paragraph(h.get_estado_display(), s['cell']),
                    Paragraph(h.fecha_deteccion.strftime('%d/%m/%Y'), s['cell']),
                    Paragraph(h.reportado_por.username if h.reportado_por else '—', s['cell']),
                ])
            widths = [1.1 * inch, 2.35 * inch, 0.95 * inch, 0.85 * inch, 0.75 * inch, 1.5 * inch]
            table = Table(data, colWidths=widths, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HEADER_BG),
                ('BOX', (0, 0), (-1, -1), 0.75, BORDER_COLOR),
                ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                ('PADDING', (0, 0), (-1, -1), 5),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, SUBHEADER_BG]),
            ]))
            elements.append(table)
        else:
            elements.append(Paragraph("No se han registrado hallazgos de auditoría a la fecha.", s['value_left']))

        build_signature_block(elements, [
            ("ELABORADO POR", "Auditor / Especialista de Fiscalización"),
            ("REVISADO POR", "Dirección de Bienes Públicos"),
            ("APROBADO POR", "Control Interno"),
        ])

        doc.build(elements)
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Informe_Auditoria_Fiscalizacion.pdf"'
        return response

class LogAccesoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Vista de solo lectura para los logs de accesos y seguridad del sistema.
    """
    queryset = LogAcceso.objects.all().order_by('-fecha')
    serializer_class = LogAccesoSerializer
    permission_classes = [IsAuthenticated]

class HallazgoViewSet(viewsets.ModelViewSet):
    """
    Hallazgos de auditoría/fiscalización sobre bienes específicos. Alimentan
    directamente el Informe de Auditoría y Fiscalización en PDF.
    """
    queryset = Hallazgo.objects.select_related('bien', 'reportado_por', 'resuelto_por').all()
    serializer_class = HallazgoSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(reportado_por=self.request.user)

    @action(detail=True, methods=['post'], url_path='resolver')
    def resolver(self, request, pk=None):
        """Marca el hallazgo como resuelto, registrando quién y cuándo."""
        hallazgo = self.get_object()
        hallazgo.estado = 'RESUELTO'
        hallazgo.resuelto_por = request.user
        hallazgo.fecha_resolucion = timezone.localdate()
        hallazgo.observaciones_resolucion = request.data.get('observaciones', '')
        hallazgo.save()
        return Response(HallazgoSerializer(hallazgo).data)