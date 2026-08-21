import io
import os
import datetime
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Paleta ajustada al formato oficial DEM (grises/negro sobre blanco, como las
# plantillas Excel de la Dirección de Bienes Públicos)
HEADER_BG = colors.HexColor('#d9d9d9')     # Gris de bandas de título/encabezado
SUBHEADER_BG = colors.HexColor('#f2f2f2')  # Gris claro de sub-encabezados
BORDER_COLOR = colors.black
TEXT_COLOR = colors.black

LOGO_PATH = os.path.join(os.path.dirname(__file__), 'pdf_assets', 'dem_logo.png')

PORTRAIT_WIDTH = 7.5 * inch
LANDSCAPE_WIDTH = 10.0 * inch

ORGANISMO_CODIGO = "21"
ORGANISMO_NOMBRE = "TSJ - DIRECCIÓN EJECUTIVA DE LA MAGISTRATURA"

ART_82_LOPB = (
    "De conformidad con lo establecido en el artículo 82 del Decreto con Rango, Valor y Fuerza de Ley Orgánica de "
    "Bienes Públicos, publicada en Gaceta Oficial de la República Bolivariana de Venezuela N° 6.155 Extraordinario "
    "de fecha 19 de noviembre de 2014, el cual señala a continuación: \"Los órganos y entes del sector público "
    "deberán adecuar y perfeccionar sus métodos y procedimientos de control interno, respecto del mantenimiento, "
    "conservación y protección de sus bienes, de acuerdo con las normas que dicte la Superintendencia de Bienes "
    "Públicos. Los funcionarios públicos que tengan competencia en la conservación, mantenimiento y protección de "
    "bienes públicos, deberán llevar un sistema de registro que evidencie la cronología de los trabajos de "
    "mantenimiento y/o reparaciones dados a los bienes, especificando el detalle de los materiales utilizados y "
    "costos de los mismos.\""
)


def _styles():
    styles = getSampleStyleSheet()
    return {
        'label': ParagraphStyle('Label', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5,
                                 leading=9, textColor=TEXT_COLOR, alignment=1),
        'label_left': ParagraphStyle('LabelLeft', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5,
                                      leading=9, textColor=TEXT_COLOR, alignment=0),
        'value': ParagraphStyle('Value', parent=styles['Normal'], fontName='Helvetica', fontSize=8,
                                 leading=10, textColor=TEXT_COLOR, alignment=1),
        'value_left': ParagraphStyle('ValueLeft', parent=styles['Normal'], fontName='Helvetica', fontSize=8,
                                      leading=10, textColor=TEXT_COLOR, alignment=0),
        'cell': ParagraphStyle('Cell', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=9),
        'cell_bold': ParagraphStyle('CellBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5,
                                     leading=9),
        'legal': ParagraphStyle('Legal', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=6.5,
                                 leading=8, textColor=colors.HexColor('#404040')),
        'sig': ParagraphStyle('Sig', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=11,
                               alignment=1),
    }


def parse_marca_modelo(descripcion):
    """Extrae marca/modelo de la descripción libre del bien (convención usada al registrar)."""
    marca, modelo = "", ""
    desc_parts = (descripcion or "").split(". Marca:")
    main_desc = desc_parts[0]
    if len(desc_parts) > 1:
        m_parts = desc_parts[1].split(", Modelo:")
        marca = m_parts[0].strip()
        if len(m_parts) > 1:
            modelo = m_parts[1].split(", Condición:")[0].strip()
    return main_desc, marca, modelo


def build_pdf_header(elements, title, ref_number, date_str, division=None, width=PORTRAIT_WIDTH):
    s = _styles()
    styles = getSampleStyleSheet()
    org_width = width - 1.0 * inch - 1.5 * inch

    org_lines = "<b>DIRECCIÓN EJECUTIVA DE LA MAGISTRATURA</b><br/><b>DIRECCIÓN GENERAL DE ADMINISTRACIÓN Y FINANZAS</b><br/><b>DIRECCIÓN DE BIENES PÚBLICOS</b>"
    if division:
        org_lines += f"<br/><b>{division}</b>"

    org_style = ParagraphStyle('OrgStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5,
                                leading=10.5, textColor=TEXT_COLOR)
    ref_style = ParagraphStyle('RefStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9,
                                leading=12, textColor=TEXT_COLOR, alignment=2)

    try:
        logo = Image(LOGO_PATH, width=0.85 * inch, height=0.55 * inch)
    except Exception:
        logo = Paragraph("<b>DEM</b>", org_style)

    header_data = [[
        logo,
        Paragraph(org_lines, org_style),
        Paragraph(f"<b>N°:</b> {ref_number}<br/><b>Fecha:</b> {date_str}", ref_style),
    ]]
    header_table = Table(header_data, colWidths=[1.0 * inch, org_width, 1.5 * inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('LINEBELOW', (0, 0), (-1, 0), 1, BORDER_COLOR),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(header_table)

    title_table = Table([[Paragraph(f"<b>{title.upper()}</b>", ParagraphStyle(
        'TitleBand', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, leading=14,
        alignment=1, textColor=TEXT_COLOR))]], colWidths=[width])
    title_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HEADER_BG),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(title_table)
    elements.append(Spacer(1, 10))


def build_signature_block(elements, columns, width=PORTRAIT_WIDTH):
    """columns: lista de tuplas (etiqueta, nombre) — 2 o 3 firmas."""
    s = _styles()
    col_width = width / len(columns)
    row = [Paragraph(f"___________________________<br/><b>{label}</b><br/>{name or '—'}<br/><i>Firma y Sello</i>", s['sig'])
           for label, name in columns]
    sig_table = Table([row], colWidths=[col_width] * len(columns))
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(Spacer(1, 25))
    elements.append(KeepTogether([sig_table]))


def build_legal_note(elements, text, width=PORTRAIT_WIDTH):
    s = _styles()
    elements.append(Spacer(1, 10))
    box = Table([[Paragraph(text, s['legal'])]], colWidths=[width])
    box.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0, 0), (-1, -1), SUBHEADER_BG),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(box)


def band_row(elements, cells, widths=None, bg=HEADER_BG, total_width=PORTRAIT_WIDTH):
    s = _styles()
    widths = widths or [total_width / len(cells)] * len(cells)
    row = [Paragraph(f"<b>{c}</b>", s['label']) for c in cells]
    t = Table([row], colWidths=widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg),
        ('BOX', (0, 0), (-1, -1), 0.75, BORDER_COLOR),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(t)


def value_row(elements, cells, widths=None, total_width=PORTRAIT_WIDTH):
    s = _styles()
    widths = widths or [total_width / len(cells)] * len(cells)
    row = [Paragraph(str(c) if c not in (None, '') else '—', s['value']) for c in cells]
    t = Table([row], colWidths=widths)
    t.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.75, BORDER_COLOR),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(t)


# --------------------------------------------------------------------------
# COMPROBANTE DE REASIGNACIÓN
# --------------------------------------------------------------------------

def _reasignacion_body(elements, bienes_rows, cedente_area, cedente_cedula, cedente_nombre, cedente_cargo,
                        receptor_area, receptor_cedula, receptor_nombre, receptor_cargo, nota):
    s = _styles()

    band_row(elements, ["ORGANISMO", "UNIDAD ADMINISTRATIVA Y/O JUDICIAL CEDENTE", "UNIDAD ADMINISTRATIVA Y/O JUDICIAL RECEPTORA"],
              widths=[2.5 * inch, 2.5 * inch, 2.5 * inch])
    band_row(elements, ["CODIGO SIGECOFF", "CODIGO", "CODIGO"], bg=SUBHEADER_BG,
              widths=[2.5 * inch, 2.5 * inch, 2.5 * inch])
    value_row(elements, [ORGANISMO_CODIGO, "—", "—"], widths=[2.5 * inch, 2.5 * inch, 2.5 * inch])
    band_row(elements, ["DENOMINACION", "DENOMINACION", "DENOMINACION"], bg=SUBHEADER_BG,
              widths=[2.5 * inch, 2.5 * inch, 2.5 * inch])
    value_row(elements, [ORGANISMO_NOMBRE, cedente_area, receptor_area], widths=[2.5 * inch, 2.5 * inch, 2.5 * inch])

    elements.append(Spacer(1, 6))
    band_row(elements, ["RESPONSABLE ADMINISTRATIVO CEDENTE", "RESPONSABLE ADMINISTRATIVO RECEPTOR"],
              widths=[3.75 * inch, 3.75 * inch])
    band_row(elements, ["C.I. N°", "NOMBRE Y APELLIDO", "CARGO", "C.I. N°", "NOMBRE Y APELLIDO", "CARGO"], bg=SUBHEADER_BG,
              widths=[1.1 * inch, 1.6 * inch, 1.05 * inch, 1.1 * inch, 1.6 * inch, 1.05 * inch])
    value_row(elements, [cedente_cedula, cedente_nombre, cedente_cargo, receptor_cedula, receptor_nombre, receptor_cargo],
               widths=[1.1 * inch, 1.6 * inch, 1.05 * inch, 1.1 * inch, 1.6 * inch, 1.05 * inch])

    elements.append(Spacer(1, 10))
    header = ["N° DE BIEN", "DESCRIPCIÓN", "MARCA", "MODELO", "SERIAL", "CONCEPTO", "CONDICIÓN FÍSICA"]
    data = [[Paragraph(f"<b>{h}</b>", s['cell_bold']) for h in header]]
    for r in bienes_rows:
        data.append([Paragraph(str(v) if v else '—', s['cell']) for v in r])
    widths = [0.85 * inch, 2.7 * inch, 0.75 * inch, 0.75 * inch, 0.85 * inch, 0.75 * inch, 0.85 * inch]
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

    if nota:
        elements.append(Spacer(1, 8))
        elements.append(Paragraph(f"<b>NOTA:</b> {nota}", s['value_left']))


def generate_reasignacion_pdf(buffer, traza):
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    elements = []
    build_pdf_header(elements, "Comprobante de Reasignación", f"REAS-{traza.id}", traza.fecha.strftime("%d/%m/%Y"))

    cedente_area = traza.area_origen.nombre if traza.area_origen else "Depósito Central"
    receptor_area = traza.area_destino.nombre if traza.area_destino else "—"
    u_o, u_d = traza.funcionario_origen, traza.funcionario_destino
    b = traza.bien
    main_desc, marca, modelo = parse_marca_modelo(b.descripcion)

    _reasignacion_body(
        elements,
        [[b.codigo_inventario, main_desc, marca, modelo, b.serial_fabrica, "Reasignación", ""]],
        cedente_area, u_o.cedula if u_o else "—", u_o.get_full_name() if u_o else "—", (u_o.cargo if u_o else None),
        receptor_area, u_d.cedula if u_d else "—", u_d.get_full_name() if u_d else "—", (u_d.cargo if u_d else None),
        traza.motivo,
    )

    build_signature_block(elements, [
        ("RESPONSABLE ADMINISTRATIVO CEDENTE", u_o.get_full_name() if u_o else "—"),
        ("DIRECCIÓN DE BIENES PÚBLICOS", "Dirección de Bienes Públicos DEM"),
        ("RESPONSABLE ADMINISTRATIVO RECEPTOR", u_d.get_full_name() if u_d else "—"),
    ])
    doc.build(elements)


def generate_multi_reasignacion_pdf(buffer, trazas, cedente_nombre, receptor_nombre):
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    elements = []

    first = trazas[0] if trazas else None
    es_masivo = len(trazas) != 1
    ref_num = f"REAS-MAS-{first.id}" if (first and es_masivo) else f"REAS-{first.id}" if first else "REAS"
    date_str = first.fecha.strftime("%d/%m/%Y") if first else datetime.date.today().strftime("%d/%m/%Y")
    titulo = "Comprobante de Reasignación (Masivo)" if es_masivo else "Comprobante de Reasignación"
    build_pdf_header(elements, titulo, ref_num, date_str)

    cedente_area = first.area_origen.nombre if (first and first.area_origen) else "Depósito Central"
    receptor_area = first.area_destino.nombre if (first and first.area_destino) else "—"
    u_o = first.funcionario_origen if first else None
    u_d = first.funcionario_destino if first else None

    rows = []
    for t in trazas:
        b = t.bien
        main_desc, marca, modelo = parse_marca_modelo(b.descripcion)
        rows.append([b.codigo_inventario, main_desc, marca, modelo, b.serial_fabrica, "Reasignación", ""])

    _reasignacion_body(
        elements, rows,
        cedente_area, (u_o.cedula if u_o else "—"), (u_o.get_full_name() if u_o else cedente_nombre), (u_o.cargo if u_o else None),
        receptor_area, (u_d.cedula if u_d else "—"), (u_d.get_full_name() if u_d else receptor_nombre), (u_d.cargo if u_d else None),
        first.motivo if first else None,
    )

    build_signature_block(elements, [
        ("RESPONSABLE ADMINISTRATIVO CEDENTE", u_o.get_full_name() if u_o else cedente_nombre),
        ("DIRECCIÓN DE BIENES PÚBLICOS", "Dirección de Bienes Públicos DEM"),
        ("RESPONSABLE ADMINISTRATIVO RECEPTOR", u_d.get_full_name() if u_d else receptor_nombre),
    ])
    doc.build(elements)


# --------------------------------------------------------------------------
# FICHA DE MANTENIMIENTO DE BIENES MUEBLES
# --------------------------------------------------------------------------

def _mantenimiento_header_block(elements, sede_nombre, area_nombre):
    s = _styles()
    band_row(elements, ["CÓDIGO DEL ÓRGANO O ENTE<br/>SIGECOFF O RGBP", "NOMBRE DEL ÓRGANO O ENTE",
                          "¿TIENE DISPONIBILIDAD<br/>PRESUPUESTARIA?", "¿INFORMÓ A LA<br/>SUDEBIP?"],
              widths=[1.6 * inch, 3.1 * inch, 1.4 * inch, 1.4 * inch])
    value_row(elements, [ORGANISMO_CODIGO, ORGANISMO_NOMBRE, "SI ( )   NO ( )", "SI ( )   NO ( )"],
               widths=[1.6 * inch, 3.1 * inch, 1.4 * inch, 1.4 * inch])

    band_row(elements, ["RESPONSABLE ADMINISTRATIVO", "UNIDAD ADMINISTRATIVA O JUDICIAL"], bg=SUBHEADER_BG,
              widths=[3.75 * inch, 3.75 * inch])
    value_row(elements, [area_nombre or "—", sede_nombre or "—"], widths=[3.75 * inch, 3.75 * inch])


def generate_ficha_mantenimiento_pdf(buffer, mant):
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    elements = []
    build_pdf_header(elements, "Ficha de Mantenimiento de Bienes Muebles", mant.numero_ficha,
                      mant.fecha_ficha.strftime("%d/%m/%Y"), division="DIVISIÓN DE BIENES MUEBLES")

    asignacion_activa = mant.bien.asignaciones.filter(activa=True).first()
    area_nombre = asignacion_activa.area.nombre if asignacion_activa else None
    _mantenimiento_header_block(elements, mant.bien.sede.nombre, area_nombre)

    elements.append(Spacer(1, 8))
    s = _styles()
    band_row(elements, ["ESPECIFICACIÓN DEL BIEN", "CÓDIGO DEL BIEN", "TIPO DE<br/>MANTENIMIENTO", "ACTIVIDAD REALIZADA",
                          "MATERIALES EMPLEADOS", "N° FACTURA", "COSTO", "FECHA MANTENIMIENTO"],
              widths=[1.2 * inch, 0.8 * inch, 0.75 * inch, 1.35 * inch, 1.05 * inch, 0.65 * inch, 0.6 * inch, 1.1 * inch])
    value_row(elements, [
        mant.bien.nombre, mant.bien.codigo_inventario, mant.tipo_mantenimiento, mant.actividad_realizada,
        mant.materiales_empleados or "—", mant.numero_factura, f"{float(mant.costo):.2f}",
        mant.fecha_mantenimiento.strftime("%d/%m/%Y"),
    ], widths=[1.2 * inch, 0.8 * inch, 0.75 * inch, 1.35 * inch, 1.05 * inch, 0.65 * inch, 0.6 * inch, 1.1 * inch])

    build_legal_note(elements, ART_82_LOPB)

    if mant.nota:
        elements.append(Spacer(1, 8))
        elements.append(Paragraph(f"<b>NOTA:</b> {mant.nota}", s['value_left']))

    build_signature_block(elements, [
        ("ELABORADO POR", mant.reparado_por),
        ("CONFORMADO POR", mant.conformado_por),
        ("RESPONSABLE PATRIMONIAL DE USO", mant.responsable_administrativo),
    ])
    doc.build(elements)


def generate_multi_mantenimiento_pdf(buffer, mantenimientos):
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    elements = []

    first = mantenimientos[0] if mantenimientos else None
    ref_num = first.numero_ficha if first else "MANT-MAS"
    date_str = first.fecha_ficha.strftime("%d/%m/%Y") if first else datetime.date.today().strftime("%d/%m/%Y")
    build_pdf_header(elements, "Ficha Consolidada de Mantenimiento de Bienes Muebles", ref_num, date_str,
                      division="DIVISIÓN DE BIENES MUEBLES")

    sede_nombre = first.bien.sede.nombre if first else "—"
    asignacion_activa = first.bien.asignaciones.filter(activa=True).first() if first else None
    area_nombre = asignacion_activa.area.nombre if asignacion_activa else None
    _mantenimiento_header_block(elements, sede_nombre, area_nombre)

    elements.append(Spacer(1, 10))
    s = _styles()
    header = ["CÓD. BIEN", "NOMBRE DEL BIEN", "ACTIVIDAD REALIZADA", "MATERIALES EMPLEADOS", "COSTO (Bs)"]
    data = [[Paragraph(f"<b>{h}</b>", s['cell_bold']) for h in header]]
    total_cost = 0.0
    for m in mantenimientos:
        cost_val = float(m.costo) if m.costo else 0.0
        total_cost += cost_val
        data.append([
            Paragraph(m.bien.codigo_inventario, s['cell']),
            Paragraph(m.bien.nombre, s['cell']),
            Paragraph(m.actividad_realizada or "—", s['cell']),
            Paragraph(m.materiales_empleados or "—", s['cell']),
            Paragraph(f"{cost_val:.2f}", s['cell']),
        ])
    data.append([Paragraph("<b>TOTAL</b>", s['cell_bold']), "", "", "", Paragraph(f"<b>{total_cost:.2f}</b>", s['cell_bold'])])

    widths = [1.1 * inch, 1.9 * inch, 2.1 * inch, 1.6 * inch, 0.8 * inch]
    table = Table(data, colWidths=widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HEADER_BG),
        ('BACKGROUND', (0, -1), (-1, -1), SUBHEADER_BG),
        ('SPAN', (0, -1), (3, -1)),
        ('BOX', (0, 0), (-1, -1), 0.75, BORDER_COLOR),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, SUBHEADER_BG]),
    ]))
    elements.append(table)

    build_legal_note(elements, ART_82_LOPB)

    if first and first.nota:
        elements.append(Spacer(1, 8))
        elements.append(Paragraph(f"<b>NOTA:</b> {first.nota}", s['value_left']))

    build_signature_block(elements, [
        ("ELABORADO POR", first.reparado_por if first else "—"),
        ("CONFORMADO POR", first.conformado_por if first else "—"),
        ("RESPONSABLE PATRIMONIAL DE USO", first.responsable_administrativo if first else "—"),
    ])
    doc.build(elements)


# --------------------------------------------------------------------------
# INVENTARIO GENERAL DE BIENES
# --------------------------------------------------------------------------

def generate_inventario_general_pdf(buffer, bienes):
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    build_pdf_header(elements, "Inventario de Bienes Públicos", "INV-GRAL", datetime.date.today().strftime("%d/%m/%Y"),
                      width=LANDSCAPE_WIDTH)

    s = _styles()
    header = ["N° DE BIEN", "DESCRIPCIÓN", "MARCA", "MODELO", "SERIAL", "SEDE", "UBICACIÓN / ÁREA", "ESTADO"]
    data = [[Paragraph(f"<b>{h}</b>", s['cell_bold']) for h in header]]

    for b in bienes:
        main_desc, marca, modelo = parse_marca_modelo(b.descripcion)
        asignacion_activa = b.asignaciones.filter(activa=True).first()
        ubicacion = asignacion_activa.area.nombre if asignacion_activa else "Sin asignar"
        data.append([
            Paragraph(f"<b>{b.codigo_inventario}</b>", s['cell']),
            Paragraph(main_desc, s['cell']),
            Paragraph(marca or "—", s['cell']),
            Paragraph(modelo or "—", s['cell']),
            Paragraph(b.serial_fabrica or "—", s['cell']),
            Paragraph(b.sede.nombre, s['cell']),
            Paragraph(ubicacion, s['cell']),
            Paragraph(b.estado, s['cell']),
        ])

    widths = [1.0 * inch, 2.8 * inch, 1.0 * inch, 1.0 * inch, 1.0 * inch, 1.1 * inch, 1.2 * inch, 0.8 * inch]
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

    build_signature_block(elements, [
        ("ELABORADO POR", "Analista de Inventario"),
        ("CONFORMADO POR", "Jefe de Departamento"),
        ("APROBADO POR", "Director de Bienes Públicos"),
    ], width=LANDSCAPE_WIDTH)
    doc.build(elements)


# --------------------------------------------------------------------------
# RELACIÓN DETALLADA DE LOS BIENES A DESINCORPORAR
# --------------------------------------------------------------------------

def generate_multi_desincorporacion_pdf(buffer, trazas, motivo):
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)
    elements = []

    first = trazas[0] if trazas else None
    ref_num = f"DES-MAS-{first.id}" if (first and len(trazas) != 1) else f"DES-{first.id}" if first else "DES"
    date_str = first.fecha.strftime("%d/%m/%Y") if first else datetime.date.today().strftime("%d/%m/%Y")
    build_pdf_header(elements, "Relación Detallada de los Bienes a Desincorporar", ref_num, date_str,
                      division="DIVISIÓN DE DESINCORPORACIÓN", width=LANDSCAPE_WIDTH)

    s = _styles()
    band_row(elements, ["ORGANISMO", "MOTIVO DE LA DESINCORPORACIÓN"], widths=[2.5 * inch, 7.5 * inch])
    value_row(elements, [ORGANISMO_NOMBRE, motivo], widths=[2.5 * inch, 7.5 * inch])
    elements.append(Spacer(1, 10))

    header = ["ITEM", "N° DE BIEN NACIONAL", "DESCRIPCIÓN DEL BIEN", "MARCA", "MODELO", "SERIAL", "UBICACIÓN DE PROCEDENCIA",
               "RESPONSABLE PATRIMONIAL"]
    data = [[Paragraph(f"<b>{h}</b>", s['cell_bold']) for h in header]]
    for idx, t in enumerate(trazas, start=1):
        b = t.bien
        main_desc, marca, modelo = parse_marca_modelo(b.descripcion)
        sede_name = t.sede_origen.nombre if t.sede_origen else (b.sede.nombre if b.sede else "—")
        responsable = t.funcionario_origen.get_full_name() if t.funcionario_origen else "—"
        data.append([
            Paragraph(str(idx), s['cell']),
            Paragraph(f"<b>{b.codigo_inventario}</b>", s['cell']),
            Paragraph(main_desc, s['cell']),
            Paragraph(marca or "—", s['cell']),
            Paragraph(modelo or "—", s['cell']),
            Paragraph(b.serial_fabrica or "—", s['cell']),
            Paragraph(sede_name, s['cell']),
            Paragraph(responsable, s['cell']),
        ])

    widths = [0.45 * inch, 1.05 * inch, 2.55 * inch, 0.9 * inch, 0.9 * inch, 1.05 * inch, 1.35 * inch, 1.35 * inch]
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

    build_legal_note(elements,
        "De conformidad con lo establecido en el artículo 84 del Decreto con Rango, Valor y Fuerza de Ley Orgánica "
        "de Bienes Públicos: \"Los órganos y entes del sector público deberán enajenar los bienes públicos de su "
        "propiedad que no fueren necesarios para el cumplimiento de sus finalidades y los que hubiesen sido "
        "desincorporados por obsolescencia o deterioro, conforme a los términos establecidos en el presente decreto "
        "con Rango, Valor y Fuerza de Ley Orgánica, en lo que le sea aplicable.\"", width=LANDSCAPE_WIDTH)

    build_signature_block(elements, [
        ("ANALISTA DE DESINCORPORACIÓN", "División de Bienes Muebles"),
        ("REVISOR DE CONTROL", "Dirección de Bienes Públicos"),
        ("RESPONSABLE PATRIMONIAL", "Director de Bienes Públicos"),
    ], width=LANDSCAPE_WIDTH)
    doc.build(elements)


# --------------------------------------------------------------------------
# CONTROL DE INCORPORACIONES
# --------------------------------------------------------------------------

def generate_incorporacion_pdf(buffer, oc, bienes):
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    build_pdf_header(elements, "Control de Incorporaciones", oc.numero_orden, oc.fecha_llegada.strftime("%d/%m/%Y"),
                      width=LANDSCAPE_WIDTH)

    s = _styles()
    band_row(elements, ["N° ORDEN DE COMPRA", "FECHA DE LA ORDEN", "PROVEEDOR / ENTE DONANTE",
                          "N° DE FACTURA", "FECHA DE EMISIÓN", "MONTO TOTAL ($)"],
              widths=[1.3 * inch, 1.2 * inch, 3.0 * inch, 1.2 * inch, 1.2 * inch, 1.5 * inch])

    total = sum((b.valor_adquisicion or 0) for b in bienes)
    value_row(elements, [
        oc.numero_orden, oc.fecha_llegada.strftime("%d/%m/%Y"), oc.proveedor, "—",
        oc.fecha_llegada.strftime("%d/%m/%Y"), f"{total:.2f}",
    ], widths=[1.3 * inch, 1.2 * inch, 3.0 * inch, 1.2 * inch, 1.2 * inch, 1.5 * inch])

    elements.append(Spacer(1, 10))
    band_row(elements, ["BIENES ADQUIRIDOS"], widths=[9.4 * inch])

    header = ["N° DE BIEN", "DESCRIPCIÓN", "MARCA", "MODELO", "SERIAL", "DESTINO", "PRECIO UNITARIO ($)"]
    data = [[Paragraph(f"<b>{h}</b>", s['cell_bold']) for h in header]]
    for b in bienes:
        main_desc, marca, modelo = parse_marca_modelo(b.descripcion)
        data.append([
            Paragraph(f"<b>{b.codigo_inventario}</b>", s['cell']),
            Paragraph(main_desc, s['cell']),
            Paragraph(marca or "—", s['cell']),
            Paragraph(modelo or "—", s['cell']),
            Paragraph(b.serial_fabrica or "—", s['cell']),
            Paragraph(b.sede.nombre, s['cell']),
            Paragraph(f"{b.valor_adquisicion}", s['cell']),
        ])

    widths = [1.1 * inch, 2.8 * inch, 1.1 * inch, 1.1 * inch, 1.1 * inch, 1.1 * inch, 1.3 * inch]
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

    build_signature_block(elements, [
        ("ELABORADO POR", "Dirección de Bienes Públicos"),
        ("REVISADO POR", "Responsable Administrativo"),
        ("APROBADO POR", "Director de Bienes Públicos"),
    ], width=LANDSCAPE_WIDTH)
    doc.build(elements)
