from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.http import HttpResponse
from .models import LogBien, LogAcceso
from .serializers import LogBienSerializer, LogAccesoSerializer

class LogBienViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Vista de solo lectura para los logs de bienes.
    """
    queryset = LogBien.objects.all().order_by('-fecha')
    serializer_class = LogBienSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='reporte-pdf')
    def reporte_pdf(self, request):
        """Genera un reporte PDF de todas las observaciones de auditoría/hallazgos."""
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        import io

        logs = LogBien.objects.all().order_by('-fecha')[:100]

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("DIRECCIÓN EJECUTIVA DE LA MAGISTRATURA (DEM)", styles['Heading3']))
        elements.append(Paragraph("INFORME DE FISCALIZACIÓN Y AUDITORÍA DE BIENES PÚBLICOS", styles['Title']))
        elements.append(Spacer(1, 12))
        
        # Resumen general de inventario
        from apps.inventario.models import Bien
        total_bienes = Bien.objects.count()
        bienes_asignados = Bien.objects.filter(estado='ACTIVO').count()
        bienes_sin_asignar = Bien.objects.filter(estado='INACTIVO').count()
        bienes_desincorporados = Bien.objects.filter(estado='DESINCORPORADO').count()

        elements.append(Paragraph("Resumen de Inventario Fiscalizado:", styles['Heading2']))
        elements.append(Paragraph(f"<b>Total Bienes:</b> {total_bienes}", styles['Normal']))
        elements.append(Paragraph(f"<b>Bienes Asignados:</b> {bienes_asignados} (Bien asignado 🟢)", styles['Normal']))
        elements.append(Paragraph(f"<b>Bienes Sin Asignar:</b> {bienes_sin_asignar} (Bien sin asignar 🟡)", styles['Normal']))
        elements.append(Paragraph(f"<b>Bienes Desincorporados:</b> {bienes_desincorporados} (Desincorporado 🔴)", styles['Normal']))
        elements.append(Spacer(1, 15))

        elements.append(Paragraph("Trazabilidad Reciente de Fiscalización:", styles['Heading2']))
        if logs.exists():
            data = [['Bien Código', 'Acción', 'Detalles', 'Fecha']]
            for l in logs:
                bien_cod = l.bien.codigo_inventario if l.bien else '—'
                data.append([bien_cod, l.accion, l.detalles or '—', l.fecha.strftime('%d/%m/%Y')])
            
            table = Table(data, colWidths=[110, 80, 240, 70])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(table)
        else:
            elements.append(Paragraph("No se registran hallazgos ni observaciones de inventario en el historial.", styles['Normal']))

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