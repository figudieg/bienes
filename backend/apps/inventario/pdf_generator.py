import io
import datetime
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Custom color palette matching premium dark/navy theme of the system
PRIMARY_COLOR = colors.HexColor('#1a252f')    # Deep Navy
SECONDARY_COLOR = colors.HexColor('#2c3e50')  # Lighter Slate
BORDER_COLOR = colors.HexColor('#bdc3c7')     # Light Gray
TEXT_COLOR = colors.HexColor('#2c3e50')       # Dark Text

def build_pdf_header(elements, title, ref_number, date_str):
    styles = getSampleStyleSheet()
    
    # Custom heading styles
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        textColor=PRIMARY_COLOR,
        alignment=0 # Left
    )
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=16,
        textColor=PRIMARY_COLOR,
        alignment=1 # Center
    )

    ref_style = ParagraphStyle(
        'RefStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        textColor=colors.HexColor('#c0392b'), # Red-ish accents
        alignment=2 # Right
    )

    # 3-column top header table: Org logo text, Title/Banner, Ref info
    header_data = [
        [
            Paragraph("<b>REPÚBLICA BOLIVARIANA DE VENEZUELA</b><br/>DIRECCIÓN EJECUTIVA DE LA MAGISTRATURA<br/>DIRECCIÓN DE BIENES PÚBLICOS", header_style),
            "",
            Paragraph(f"<b>N°:</b> {ref_number}<br/><b>Fecha:</b> {date_str}", ref_style)
        ]
    ]
    
    header_table = Table(header_data, colWidths=[3.5*inch, 1.5*inch, 2.0*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 15))
    
    # Title banner
    elements.append(Paragraph(title.upper(), title_style))
    elements.append(Spacer(1, 20))

def build_signature_block(elements, reparado_por, conformado_por, responsable_adm):
    styles = getSampleStyleSheet()
    sig_style = ParagraphStyle(
        'SigStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        alignment=1 # Center
    )
    
    sig_data = [
        ["", "", ""], # line placeholder
        [
            Paragraph(f"___________________________<br/><b>Reparado por:</b><br/>{reparado_por}", sig_style),
            Paragraph(f"___________________________<br/><b>Conformado por:</b><br/>{conformado_por}", sig_style),
            Paragraph(f"___________________________<br/><b>Responsable Administrativo:</b><br/>{responsable_adm}", sig_style)
        ]
    ]
    
    sig_table = Table(sig_data, colWidths=[2.3*inch, 2.3*inch, 2.3*inch])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    elements.append(Spacer(1, 30))
    elements.append(KeepTogether([sig_table]))

def generate_incorporacion_pdf(buffer, oc, bienes):
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    elements = []
    
    # Header
    build_pdf_header(
        elements, 
        "Comprobante de Incorporación de Bienes", 
        oc.numero_orden, 
        oc.fecha_llegada.strftime("%d/%m/%Y")
    )
    
    styles = getSampleStyleSheet()
    desc_style = ParagraphStyle(
        'DescStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10
    )
    bold_desc = ParagraphStyle(
        'BoldDesc',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11
    )

    # Organismo Details
    info_data = [
        [
            Paragraph("<b>ORGANISMO:</b> 21 - TSJ - DIRECCIÓN EJECUTIVA DE LA MAGISTRATURA", bold_desc),
            Paragraph(f"<b>PROVEEDOR/ENTE DONANTE:</b><br/>{oc.proveedor}", bold_desc)
        ]
    ]
    info_table = Table(info_data, colWidths=[4.0*inch, 3.5*inch])
    info_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 15))
    
    # Table headers
    data = [[
        Paragraph("<b>N° de Bien</b>", bold_desc),
        Paragraph("<b>Descripción</b>", bold_desc),
        Paragraph("<b>Marca</b>", bold_desc),
        Paragraph("<b>Modelo</b>", bold_desc),
        Paragraph("<b>Serial</b>", bold_desc),
        Paragraph("<b>Valor ($)</b>", bold_desc)
    ]]
    
    for b in bienes:
        # Extract metadata from description if parsed, or use defaults
        marca = ""
        modelo = ""
        # simple parsing
        desc_parts = b.descripcion.split(". Marca:")
        main_desc = desc_parts[0]
        if len(desc_parts) > 1:
            m_parts = desc_parts[1].split(", Modelo:")
            marca = m_parts[0].strip()
            if len(m_parts) > 1:
                modelo = m_parts[1].split(", Condición:")[0].strip()
                
        data.append([
            Paragraph(f"<b>{b.codigo_inventario}</b>", desc_style),
            Paragraph(main_desc, desc_style),
            Paragraph(marca or "—", desc_style),
            Paragraph(modelo or "—", desc_style),
            Paragraph(b.serial_fabrica or "—", desc_style),
            Paragraph(f"{b.valor_adquisicion}", desc_style)
        ])
        
    table = Table(data, colWidths=[1.1*inch, 2.5*inch, 1.1*inch, 1.1*inch, 1.0*inch, 0.7*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#eaeded')),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    elements.append(table)
    
    build_signature_block(elements, "Dpto. Incorporaciones", "Revisor de Bienes", "Dirección General DEM")
    doc.build(elements)

def generate_reasignacion_pdf(buffer, traza):
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    elements = []
    
    build_pdf_header(
        elements, 
        "Comprobante de Reasignación de Bienes", 
        f"REAS-{traza.id}", 
        traza.fecha.strftime("%d/%m/%Y")
    )
    
    styles = getSampleStyleSheet()
    desc_style = ParagraphStyle('DescStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10)
    bold_desc = ParagraphStyle('BoldDesc', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=11)
    
    # Cedente vs Receptor Info Table
    cedente_area = traza.area_origen.nombre if traza.area_origen else "Depósito Central"
    receptor_area = traza.area_destino.nombre if traza.area_destino else "Nueva Área"
    cedente_usr = traza.usuario_origen.get_full_name() if traza.usuario_origen else "N/A"
    receptor_usr = traza.usuario_destino.get_full_name() if traza.usuario_destino else "N/A"
    
    transfer_data = [
        [
            Paragraph("<b>UNIDAD CEDENTE</b>", bold_desc),
            Paragraph("<b>UNIDAD RECEPTORA</b>", bold_desc)
        ],
        [
            Paragraph(f"<b>Área:</b> {cedente_area}<br/><b>Responsable:</b> {cedente_usr}", desc_style),
            Paragraph(f"<b>Área:</b> {receptor_area}<br/><b>Responsable:</b> {receptor_usr}", desc_style)
        ]
    ]
    transfer_table = Table(transfer_data, colWidths=[3.75*inch, 3.75*inch])
    transfer_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#eaeded')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(transfer_table)
    elements.append(Spacer(1, 20))
    
    # Bienes Table
    b = traza.bien
    data = [
        [
            Paragraph("<b>N° de Bien</b>", bold_desc),
            Paragraph("<b>Descripción del Bien</b>", bold_desc),
            Paragraph("<b>Serial</b>", bold_desc),
            Paragraph("<b>Motivo del Movimiento</b>", bold_desc)
        ],
        [
            Paragraph(f"<b>{b.codigo_inventario}</b>", desc_style),
            Paragraph(b.nombre, desc_style),
            Paragraph(b.serial_fabrica or "—", desc_style),
            Paragraph(traza.motivo or "Reasignación interna", desc_style)
        ]
    ]
    table = Table(data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 2.0*inch])
    table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(table)
    
    build_signature_block(elements, cedente_usr, receptor_usr, "Jefe de Bienes DEM")
    doc.build(elements)

def generate_ficha_mantenimiento_pdf(buffer, mant):
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    elements = []
    
    build_pdf_header(
        elements, 
        "Ficha de Mantenimiento de Bienes Muebles", 
        mant.numero_ficha, 
        mant.fecha_ficha.strftime("%d/%m/%Y")
    )
    
    styles = getSampleStyleSheet()
    desc_style = ParagraphStyle('DescStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10)
    bold_desc = ParagraphStyle('BoldDesc', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=11)
    
    # Ente & Ubicación Info Table
    info_data = [
        [
            Paragraph(f"<b>Código del Órgano/Ente RGBP:</b> 21", desc_style),
            Paragraph(f"<b>Nombre del Órgano/Ente:</b> TSJ - DEM", desc_style)
        ],
        [
            Paragraph(f"<b>Ubicación Administrativa:</b> {mant.bien.sede.nombre}", desc_style),
            Paragraph(f"<b>Código Unidad Adm.:</b> {mant.bien.codigo_inventario}", desc_style)
        ]
    ]
    info_table = Table(info_data, colWidths=[3.75*inch, 3.75*inch])
    info_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 15))
    
    # Maintenance Details Table
    details_data = [
        [
            Paragraph("<b>Especificación del Bien</b>", bold_desc),
            Paragraph("<b>Tipo Mantenimiento</b>", bold_desc),
            Paragraph("<b>Actividad Realizada</b>", bold_desc),
            Paragraph("<b>Materiales Empleados</b>", bold_desc),
            Paragraph("<b>Factura</b>", bold_desc),
            Paragraph("<b>Costo (Bs)</b>", bold_desc)
        ],
        [
            Paragraph(mant.bien.nombre, desc_style),
            Paragraph(mant.tipo_mantenimiento, desc_style),
            Paragraph(mant.actividad_realizada, desc_style),
            Paragraph(mant.materiales_empleados or "Autogestión / Herramientas", desc_style),
            Paragraph(mant.numero_factura, desc_style),
            Paragraph(f"{mant.costo}", desc_style)
        ]
    ]
    details_table = Table(details_data, colWidths=[1.8*inch, 1.1*inch, 1.5*inch, 1.4*inch, 0.9*inch, 0.8*inch])
    details_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#eaeded')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(details_table)
    
    if mant.nota:
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(f"<b>Nota/Observación:</b> {mant.nota}", desc_style))
        
    build_signature_block(elements, mant.reparado_por, mant.conformado_por, mant.responsable_administrativo)
    doc.build(elements)

def generate_inventario_general_pdf(buffer, bienes):
    # Inventarios are wider, use landscape
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    elements = []
    
    build_pdf_header(
        elements, 
        "Inventario General de Bienes Muebles", 
        "INV-GRAL", 
        datetime.date.today().strftime("%d/%m/%Y")
    )
    
    styles = getSampleStyleSheet()
    desc_style = ParagraphStyle('DescStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=7, leading=9)
    bold_desc = ParagraphStyle('BoldDesc', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10)
    
    data = [[
        Paragraph("<b>N° de Bien</b>", bold_desc),
        Paragraph("<b>Descripción del Bien</b>", bold_desc),
        Paragraph("<b>Marca</b>", bold_desc),
        Paragraph("<b>Modelo</b>", bold_desc),
        Paragraph("<b>Serial</b>", bold_desc),
        Paragraph("<b>Sede</b>", bold_desc),
        Paragraph("<b>Estado</b>", bold_desc)
    ]]
    
    for b in bienes:
        marca = ""
        modelo = ""
        desc_parts = b.descripcion.split(". Marca:")
        main_desc = desc_parts[0]
        if len(desc_parts) > 1:
            m_parts = desc_parts[1].split(", Modelo:")
            marca = m_parts[0].strip()
            if len(m_parts) > 1:
                modelo = m_parts[1].split(", Condición:")[0].strip()
                
        data.append([
            Paragraph(f"<b>{b.codigo_inventario}</b>", desc_style),
            Paragraph(main_desc, desc_style),
            Paragraph(marca or "—", desc_style),
            Paragraph(modelo or "—", desc_style),
            Paragraph(b.serial_fabrica or "—", desc_style),
            Paragraph(b.sede.nombre, desc_style),
            Paragraph(b.estado, desc_style)
        ])
        
    table = Table(data, colWidths=[1.2*inch, 3.5*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch, 0.7*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#eaeded')),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    elements.append(table)
    
    build_signature_block(elements, "Analista de Inventario", "Jefe de Departamento", "Director de Bienes Públicos")
    doc.build(elements)

def generate_multi_reasignacion_pdf(buffer, trazas, cedente_nombre, receptor_nombre):
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    elements = []
    
    first_traza = trazas[0] if trazas else None
    ref_num = f"REAS-MAS-{first_traza.id}" if first_traza else "REAS-MAS"
    date_str = first_traza.fecha.strftime("%d/%m/%Y") if first_traza else datetime.date.today().strftime("%d/%m/%Y")
    
    build_pdf_header(
        elements, 
        "Comprobante de Reasignación de Bienes (Masivo)", 
        ref_num, 
        date_str
    )
    
    styles = getSampleStyleSheet()
    desc_style = ParagraphStyle('DescStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10)
    bold_desc = ParagraphStyle('BoldDesc', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=11)
    
    cedente_area = first_traza.area_origen.nombre if (first_traza and first_traza.area_origen) else "Depósito Central"
    receptor_area = first_traza.area_destino.nombre if (first_traza and first_traza.area_destino) else "Nueva Área"
    
    transfer_data = [
        [
            Paragraph("<b>UNIDAD CEDENTE</b>", bold_desc),
            Paragraph("<b>UNIDAD RECEPTORA</b>", bold_desc)
        ],
        [
            Paragraph(f"<b>Área:</b> {cedente_area}<br/><b>Responsable:</b> {cedente_nombre}", desc_style),
            Paragraph(f"<b>Área:</b> {receptor_area}<br/><b>Responsable:</b> {receptor_nombre}", desc_style)
        ]
    ]
    transfer_table = Table(transfer_data, colWidths=[3.75*inch, 3.75*inch])
    transfer_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#eaeded')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(transfer_table)
    elements.append(Spacer(1, 15))
    
    data = [
        [
            Paragraph("<b>Cód. Inventario</b>", bold_desc),
            Paragraph("<b>Descripción del Bien</b>", bold_desc),
            Paragraph("<b>Serial Fábrica</b>", bold_desc),
            Paragraph("<b>Motivo</b>", bold_desc)
        ]
    ]
    
    for t in trazas:
        b = t.bien
        data.append([
            Paragraph(f"<b>{b.codigo_inventario}</b>", desc_style),
            Paragraph(b.nombre, desc_style),
            Paragraph(b.serial_fabrica or "—", desc_style),
            Paragraph(t.motivo or "Reasignación interna masiva", desc_style)
        ])
        
    table = Table(data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 2.0*inch])
    table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f2f4f4')]),
    ]))
    elements.append(table)
    
    build_signature_block(elements, cedente_nombre, receptor_nombre, "Jefe de Bienes DEM")
    doc.build(elements)

def generate_multi_desincorporacion_pdf(buffer, trazas, motivo):
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    elements = []
    
    first_traza = trazas[0] if trazas else None
    ref_num = f"DES-MAS-{first_traza.id}" if first_traza else "DES-MAS"
    date_str = first_traza.fecha.strftime("%d/%m/%Y") if first_traza else datetime.date.today().strftime("%d/%m/%Y")
    
    build_pdf_header(
        elements, 
        "Comprobante de Desincorporación de Bienes Muebles", 
        ref_num, 
        date_str
    )
    
    styles = getSampleStyleSheet()
    desc_style = ParagraphStyle('DescStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10)
    bold_desc = ParagraphStyle('BoldDesc', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=11)
    
    info_data = [
        [
            Paragraph("<b>ORGANISMO:</b> 21 - TSJ - DIRECCIÓN EJECUTIVA DE LA MAGISTRATURA", bold_desc),
            Paragraph(f"<b>MOTIVO GENERAL:</b><br/>{motivo}", bold_desc)
        ]
    ]
    info_table = Table(info_data, colWidths=[4.0*inch, 3.5*inch])
    info_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 15))
    
    data = [
        [
            Paragraph("<b>Cód. Inventario</b>", bold_desc),
            Paragraph("<b>Descripción del Bien</b>", bold_desc),
            Paragraph("<b>Sede Procedencia</b>", bold_desc),
            Paragraph("<b>Serial Fábrica</b>", bold_desc)
        ]
    ]
    
    for t in trazas:
        b = t.bien
        sede_name = t.sede_origen.nombre if t.sede_origen else (b.sede.nombre if b.sede else "—")
        data.append([
            Paragraph(f"<b>{b.codigo_inventario}</b>", desc_style),
            Paragraph(b.nombre, desc_style),
            Paragraph(sede_name, desc_style),
            Paragraph(b.serial_fabrica or "—", desc_style)
        ])
        
    table = Table(data, colWidths=[1.5*inch, 2.5*inch, 1.8*inch, 1.7*inch])
    table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f5b7b1')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fdf2e9')]),
    ]))
    elements.append(table)
    
    build_signature_block(elements, "Analista de Desincorporación", "Revisor de Control", "Director de Bienes Públicos")
    doc.build(elements)

def generate_multi_mantenimiento_pdf(buffer, mantenimientos):
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    elements = []
    
    first_mant = mantenimientos[0] if mantenimientos else None
    ref_num = first_mant.numero_ficha if first_mant else "MANT-MAS"
    date_str = first_mant.fecha_ficha.strftime("%d/%m/%Y") if first_mant else datetime.date.today().strftime("%d/%m/%Y")
    
    build_pdf_header(
        elements, 
        "Ficha Consolidada de Mantenimiento de Bienes", 
        ref_num, 
        date_str
    )
    
    styles = getSampleStyleSheet()
    desc_style = ParagraphStyle('DescStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10)
    bold_desc = ParagraphStyle('BoldDesc', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=11)
    
    sede_nombre = first_mant.bien.sede.nombre if (first_mant and first_mant.bien.sede) else "Sede Central DEM"
    
    info_data = [
        [
            Paragraph("<b>ÓRGANO/ENTE:</b> TSJ - DIRECCIÓN EJECUTIVA DE LA MAGISTRATURA", desc_style),
            Paragraph(f"<b>UBICACIÓN ADMINISTRATIVA:</b> {sede_nombre}", desc_style)
        ],
        [
            Paragraph(f"<b>TIPO MANTENIMIENTO:</b> {first_mant.tipo_mantenimiento if first_mant else 'CORRECTIVO'}", desc_style),
            Paragraph(f"<b>N° FACTURA:</b> {first_mant.numero_factura if first_mant else 'Autogestión'}", desc_style)
        ]
    ]
    info_table = Table(info_data, colWidths=[3.75*inch, 3.75*inch])
    info_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 15))
    
    details_data = [
        [
            Paragraph("<b>Cód. Bien</b>", bold_desc),
            Paragraph("<b>Nombre del Bien</b>", bold_desc),
            Paragraph("<b>Actividad Realizada</b>", bold_desc),
            Paragraph("<b>Materiales Empleados</b>", bold_desc),
            Paragraph("<b>Costo (Bs)</b>", bold_desc)
        ]
    ]
    
    total_cost = 0.00
    for m in mantenimientos:
        cost_val = float(m.costo) if m.costo else 0.0
        total_cost += cost_val
        details_data.append([
            Paragraph(m.bien.codigo_inventario, desc_style),
            Paragraph(m.bien.nombre, desc_style),
            Paragraph(m.actividad_realizada or "—", desc_style),
            Paragraph(m.materiales_empleados or "—", desc_style),
            Paragraph(f"{cost_val:.2f}", desc_style)
        ])
        
    details_data.append([
        Paragraph("<b>TOTAL</b>", bold_desc),
        "", "", "",
        Paragraph(f"<b>{total_cost:.2f}</b>", bold_desc)
    ])
    
    details_table = Table(details_data, colWidths=[1.2*inch, 1.8*inch, 2.0*inch, 1.5*inch, 1.0*inch])
    details_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#eaeded')),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#eaeded')),
        ('SPAN', (0, -1), (3, -1)),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    elements.append(details_table)
    
    if first_mant and first_mant.nota:
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(f"<b>Nota/Observación General:</b> {first_mant.nota}", desc_style))
        
    reparado = first_mant.reparado_por if first_mant else "Soporte Técnico"
    conformado = first_mant.conformado_por if first_mant else "Jefe de Bienes"
    responsable = first_mant.responsable_administrativo if first_mant else "Director DEM"
    
    build_signature_block(elements, reparado, conformado, responsable)
    doc.build(elements)
