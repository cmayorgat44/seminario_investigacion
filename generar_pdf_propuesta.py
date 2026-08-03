import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        if self._pageNumber > 1:
            # Running Header
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#2C3E50"))
            self.drawString(54, 11 * inch - 36, "UNIVERSIDAD ANÁHUAC MÉXICO | MAESTRÍA EN ESTADÍSTICA")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#7F8C8D"))
            self.drawRightString(8.5 * inch - 54, 11 * inch - 36, "Protocolo de Tesis — C. G. Mayorga Tapia")
            
            # Header rule
            self.setStrokeColor(colors.HexColor("#BDC3C7"))
            self.setLineWidth(0.5)
            self.line(54, 11 * inch - 42, 8.5 * inch - 54, 11 * inch - 42)
            
            # Running Footer
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#7F8C8D"))
            self.drawString(54, 36, "Asesor: Dr. José Eluid Silva Urrutia")
            page_text = f"Página {self._pageNumber} de {page_count}"
            self.drawRightString(8.5 * inch - 54, 36, page_text)
            
            # Footer rule
            self.setStrokeColor(colors.HexColor("#BDC3C7"))
            self.setLineWidth(0.5)
            self.line(54, 48, 8.5 * inch - 54, 48)
            
        self.restoreState()

def create_proposal_pdf(output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    PRIMARY = colors.HexColor("#D35400")   # Anahuac Orange Accent
    SECONDARY = colors.HexColor("#2C3E50") # Deep Slate Navy
    TEXT_DARK = colors.HexColor("#2B2B2B") # Off-black body
    BG_LIGHT = colors.HexColor("#F8F9F9")  # Soft background
    BORDER_COLOR = colors.HexColor("#E5E7E9")
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=SECONDARY,
        alignment=TA_CENTER,
        spaceAfter=8
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=PRIMARY,
        alignment=TA_CENTER,
        spaceAfter=12
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=SECONDARY,
        spaceBefore=12,
        spaceAfter=5,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=PRIMARY,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=TEXT_DARK,
        alignment=TA_JUSTIFY,
        spaceAfter=5
    )
    
    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=12,
        bulletIndent=4,
        spaceAfter=3
    )
    
    math_style = ParagraphStyle(
        'Math_Custom',
        parent=styles['Normal'],
        fontName='Courier-Oblique',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1A5276"),
        alignment=TA_CENTER,
        spaceBefore=5,
        spaceAfter=5
    )
    
    meta_label = ParagraphStyle('MetaLabel', fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=SECONDARY)
    meta_val = ParagraphStyle('MetaVal', fontName='Helvetica', fontSize=9, leading=12, textColor=TEXT_DARK)
    
    story = []
    
    # --- HEADER BLOCK ---
    story.append(Paragraph("UNIVERSIDAD ANÁHUAC MÉXICO", ParagraphStyle('UniHeader', fontName='Helvetica-Bold', fontSize=13, leading=16, textColor=PRIMARY, alignment=TA_CENTER)))
    story.append(Paragraph("Facultad de Ciencias Actuariales &nbsp;|&nbsp; Posgrado en Estadística", ParagraphStyle('SubHeader', fontName='Helvetica', fontSize=9.5, leading=12, textColor=SECONDARY, alignment=TA_CENTER)))
    story.append(Paragraph("Maestría en Estadística — Protocolo Actualizado de Tesis", ParagraphStyle('ProgHeader', fontName='Helvetica-Oblique', fontSize=9, leading=11, textColor=colors.HexColor("#5D6D7E"), alignment=TA_CENTER)))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceBefore=0, spaceAfter=12))
    
    # --- TITLE ---
    story.append(Paragraph("PROPUESTA DE PROTOCOLO DE TESIS DE MAESTRÍA", title_style))
    story.append(Paragraph("Modelación de Factores Dinámicos y Cointegración (FAVAR-VECM) para el Pronóstico de la Presión Inmobiliaria y el Desplazamiento Demográfico en la ZMVM", subtitle_style))
    
    # --- METADATA BOX ---
    meta_data = [
        [Paragraph("<b>Alumno:</b>", meta_label), Paragraph("Carlos Guillermo Mayorga Tapia", meta_val),
         Paragraph("<b>Asesor Propuesto:</b>", meta_label), Paragraph("Dr. José Eluid Silva Urrutia", meta_val)],
        [Paragraph("<b>Programa:</b>", meta_label), Paragraph("Maestría en Estadística", meta_val),
         Paragraph("<b>Fecha Actualización:</b>", meta_label), Paragraph("Agosto de 2026 (Versión 2.0)", meta_val)],
        [Paragraph("<b>Arquitectura BD:</b>", meta_label), Paragraph("DuckDB Relacional / 3NF / Esquema Estrella", meta_val),
         Paragraph("<b>Validación QA:</b>", meta_label), Paragraph("Detección MAD, Pruebas ADF y KPSS", meta_val)]
    ]
    meta_table = Table(meta_data, colWidths=[1.1*inch, 2.4*inch, 1.3*inch, 2.2*inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 12))
    
    # SECCIONES
    story.append(Paragraph("1. INTRODUCCIÓN Y CONTEXTO METROPOLITANO", h1_style))
    story.append(Paragraph(
        "La Zona Metropolitana del Valle de México (ZMVM), con más de 21 millones de habitantes, vive una intensa reestructuración urbana. Sectores centrales experimentan una marcada gentrificación comercial y expansión del alquiler vacacional de corta estancia. Frente al esquema determinista decenal del CONAPO, esta tesis propone un marco probabilístico de **Series de Tiempo de Alta Dimensión** (FAVAR-VECM).",
        body_style
    ))
    
    story.append(Paragraph("2. HALLAZGOS EMPÍRICOS PRELIMINARES Y VIABILIDAD DE DATOS", h1_style))
    story.append(Paragraph(
        "Como parte del avance técnico, se realizó la descarga e inspección del dataset completo de <b>Inside Airbnb CDMX</b> (31,430 propiedades activas), confirmando patrones empíricos de sustitución de vivienda habitacional:",
        body_style
    ))
    
    ab_data = [
        [Paragraph("<b>Alcaldía</b>", ParagraphStyle('TH1', fontName='Helvetica-Bold', fontSize=8.5, textColor=SECONDARY)),
         Paragraph("<b>Propiedades Activas</b>", ParagraphStyle('TH2', fontName='Helvetica-Bold', fontSize=8.5, textColor=SECONDARY)),
         Paragraph("<b>% del Total CDMX</b>", ParagraphStyle('TH3', fontName='Helvetica-Bold', fontSize=8.5, textColor=SECONDARY)),
         Paragraph("<b>Precio Mediano/Noche (MXN)</b>", ParagraphStyle('TH4', fontName='Helvetica-Bold', fontSize=8.5, textColor=SECONDARY))],
        [Paragraph("Cuauhtémoc", body_style), Paragraph("14,449", body_style), Paragraph("45.97%", body_style), Paragraph("$1,979.00", body_style)],
        [Paragraph("Miguel Hidalgo", body_style), Paragraph("4,870", body_style), Paragraph("15.49%", body_style), Paragraph("$2,211.50", body_style)],
        [Paragraph("Benito Juárez", body_style), Paragraph("3,623", body_style), Paragraph("11.53%", body_style), Paragraph("$1,398.00", body_style)],
        [Paragraph("Coyoacán", body_style), Paragraph("2,458", body_style), Paragraph("7.82%", body_style), Paragraph("$1,598.00", body_style)],
    ]
    ab_table = Table(ab_data, colWidths=[1.8*inch, 1.7*inch, 1.5*inch, 2.0*inch])
    ab_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(ab_table)
    story.append(Spacer(1, 6))
    story.append(Paragraph("<i>Nota: El 66.82% (21,000 unidades) corresponde a viviendas/departamentos completos extraídos del mercado residencial permanente.</i>", ParagraphStyle('Note', fontName='Helvetica-Oblique', fontSize=8, textColor=colors.HexColor("#5D6D7E"))))
    
    story.append(Paragraph("3. ARQUITECTURA DE DATOS Y PRUEBAS DE ROBUSTEZ (QA)", h1_style))
    story.append(Paragraph(
        "Se implementó una base de datos relacional analítica local en <b>DuckDB (3NF / Esquema Estrella)</b> (<code>processed_data/tesis_zmvm.duckdb</code>) articulada mediante <code>dim_alcaldia</code>, <code>dim_tiempo</code> (80 trimestres 2005Q1-2024Q4) y tablas de hechos. Asimismo, se integró el módulo <code>src/data_quality/validator.py</code> para ejecutar validación de continuidad temporal, detección robusta de outliers vía MAD y pruebas cruzadas de integrabilidad estocástica ADF y KPSS.",
        body_style
    ))
    
    story.append(Paragraph("4. FORMULACIÓN MATEMÁTICA Y MODELO FAVAR-VECM", h1_style))
    story.append(Paragraph("X_t = &Lambda; F_t + e_t &nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp; &Delta;W_t = &Pi; W_{t-1} + &sum;_{i=1}^{p-1} &Gamma;_i &Delta;W_{t-i} + &epsilon;_t", math_style))
    story.append(Paragraph(
        "donde &Hat;F<sub>t</sub> representa los factores latentes de presión inmobiliaria y comercial extraídos vía DFM, y &Pi; = &alpha;&beta;' captura los vectores de cointegración entre precios, alquileres de corta estancia y movilidad laboral de la ENOE.",
        body_style
    ))
    
    story.append(Paragraph("5. CRONOGRAMA DE TRABAJO (12 MESES)", h1_style))
    story.append(Paragraph("Fase I (Meses 1-2): Armonización de series. | Fase II (Meses 3-4): DFM e Integrabilidad. | Fase III (Meses 5-6): Cointegración Johansen y FAVAR. | Fase IV (Meses 7-8): IRF y FEVD. | Fase V (Meses 9-10): Backtesting fuera de muestra. | Fase VI (Meses 11-12): Redacción y Defensa.", body_style))
    
    story.append(Spacer(1, 15))
    sig_data = [
        [Paragraph("____________________________________________<br/><b>Carlos Guillermo Mayorga Tapia</b><br/>Alumno — Maestría en Estadística", ParagraphStyle('Sig1', fontName='Helvetica', fontSize=8.5, alignment=TA_CENTER)),
         Paragraph("____________________________________________<br/><b>Dr. José Eluid Silva Urrutia</b><br/>Asesor / Director de Tesis", ParagraphStyle('Sig2', fontName='Helvetica', fontSize=8.5, alignment=TA_CENTER))]
    ]
    sig_table = Table(sig_data, colWidths=[3.5*inch, 3.5*inch])
    story.append(KeepTogether(sig_table))
    
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF generado exitosamente en: {output_path}")

if __name__ == "__main__":
    out_pdf = "/Users/carlosmayorga/github/anahuac/seminario_investigacion/Propuesta_Tesis_Carlos_Mayorga_Anahuac.pdf"
    if len(sys.argv) > 1:
        out_pdf = sys.argv[1]
    create_proposal_pdf(out_pdf)
