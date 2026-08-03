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
            self.drawRightString(8.5 * inch - 54, 11 * inch - 36, "Protocolo Extenso de Tesis — C. G. Mayorga Tapia")
            
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
        fontSize=17,
        leading=21,
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
        fontSize=11.5,
        leading=15,
        textColor=SECONDARY,
        spaceBefore=12,
        spaceAfter=4,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
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
        fontSize=8.5,
        leading=12.5,
        textColor=TEXT_DARK,
        alignment=TA_JUSTIFY,
        spaceAfter=4.5
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
    
    meta_label = ParagraphStyle('MetaLabel', fontName='Helvetica-Bold', fontSize=8.5, leading=11.5, textColor=SECONDARY)
    meta_val = ParagraphStyle('MetaVal', fontName='Helvetica', fontSize=8.5, leading=11.5, textColor=TEXT_DARK)
    
    story = []
    
    # --- HEADER BLOCK ---
    story.append(Paragraph("UNIVERSIDAD ANÁHUAC MÉXICO", ParagraphStyle('UniHeader', fontName='Helvetica-Bold', fontSize=13, leading=16, textColor=PRIMARY, alignment=TA_CENTER)))
    story.append(Paragraph("Facultad de Ciencias Actuariales &nbsp;|&nbsp; Posgrado en Estadística", ParagraphStyle('SubHeader', fontName='Helvetica', fontSize=9.5, leading=12, textColor=SECONDARY, alignment=TA_CENTER)))
    story.append(Paragraph("Maestría en Estadística — Protocolo Extenso de Tesis (Versión 3.0)", ParagraphStyle('ProgHeader', fontName='Helvetica-Oblique', fontSize=9, leading=11, textColor=colors.HexColor("#5D6D7E"), alignment=TA_CENTER)))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceBefore=0, spaceAfter=10))
    
    # --- TITLE ---
    story.append(Paragraph("PROPUESTA DE PROTOCOLO DE TESIS DE MAESTRÍA", title_style))
    story.append(Paragraph("Modelación de Factores Dinámicos y Cointegración (FAVAR-VECM) para el Pronóstico de la Presión Inmobiliaria y el Desplazamiento Demográfico en la ZMVM", subtitle_style))
    
    # --- METADATA BOX ---
    meta_data = [
        [Paragraph("<b>Alumno:</b>", meta_label), Paragraph("Carlos Guillermo Mayorga Tapia", meta_val),
         Paragraph("<b>Asesor Propuesto:</b>", meta_label), Paragraph("Dr. José Eluid Silva Urrutia", meta_val)],
        [Paragraph("<b>Programa:</b>", meta_label), Paragraph("Maestría en Estadística", meta_val),
         Paragraph("<b>Fecha Actualización:</b>", meta_label), Paragraph("Agosto de 2026 (Versión 3.0)", meta_val)],
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
    story.append(Spacer(1, 10))
    
    # 1. INTRODUCCIÓN Y CONTEXTO
    story.append(Paragraph("1. INTRODUCCIÓN Y CONTEXTO SOCIOESPACIAL METROPOLITANO", h1_style))
    story.append(Paragraph(
        "La Zona Metropolitana del Valle de México (ZMVM) concentra una población superior a los 21 millones de habitantes distribuida entre las 16 alcaldías de la Ciudad de México y 59 municipios conurbados del Estado de México e Hidalgo. En los últimos lustros, las áreas centrales de esta metrópoli han experimentado una drástica reestructuración sociodemográfica caracterizada por la apreciación del suelo, la gentrificación comercial y una rápida expansión del alquiler vacacional de corta estancia (ej. Airbnb).",
        body_style
    ))
    story.append(Paragraph(
        "Frente al esquema determinista decenal del Consejo Nacional de Población (CONAPO) basado en el Método de Componentes Demográficos (MCD), esta investigación plantea abordar el desplazamiento poblacional desde un marco estocástico de <b>Series de Tiempo de Alta Dimensión</b> (FAVAR-VECM). Se busca integrar indicadores inmobiliarios (SHF), actividad comercial (DENUE-INEGI), alojamiento vacacional (Airbnb) y microdatos de empleo/migración de la Encuesta Nacional de Ocupación y Empleo (ENOE-INEGI).",
        body_style
    ))
    
    # 2. PLANTEAMIENTO DEL PROBLEMA E HIPÓTESIS
    story.append(Paragraph("2. PLANTEAMIENTO DEL PROBLEMA E HIPÓTESIS", h1_style))
    story.append(Paragraph(
        "Existe una brecha metodológica sustancial en México: los censos decenales no ofrecen la resolución temporal continua para guiar políticas públicas urbanas, mientras que los índices inmobiliarios de alta frecuencia raras veces se conectan formalmente con los flujos de la fuerza laboral.",
        body_style
    ))
    story.append(Paragraph("<b>Hipótesis Principal (H1):</b> La presión de precios de vivienda (Índice SHF) y la densidad de servicios comerciales gentrificadores y rentas cortas (DENUE/Airbnb) mantienen una relación de cointegración estocástica de largo plazo con la tasa de saldo migratorio neto negativo de la población trabajadora de ingresos medios y bajos en las alcaldías centrales de la ZMVM.", bullet_style))
    story.append(Paragraph("<b>Hipótesis Secundaria (H2):</b> La reducción de dimensionalidad mediante un Modelo de Factores Dinámicos (DFM) extrae factores latentes de <i>Presión Inmobiliaria</i> (&Hat;F<sub>1,t</sub>) y <i>Gentrificación Comercial</i> (&Hat;F<sub>2,t</sub>) que reducen el error cuadrático medio de pronóstico fuera de muestra (RMSE) frente a modelos ARIMA y VAR tradicionales.", bullet_style))
    story.append(Paragraph("<b>Hipótesis Secundaria (H3):</b> Los choques inmobiliarios (vía Funciones de Impulso-Respuesta, IRF) presentan una respuesta asimétrica, alcanzando su pico de desplazamiento poblacional entre el cuarto y el octavo trimestre posterior al choque.", bullet_style))

    # 3. OBJETIVOS
    story.append(Paragraph("3. OBJETIVOS DE INVESTIGACIÓN", h1_style))
    story.append(Paragraph("<b>Objetivo General:</b> Desarrollar, estimar y evaluar un marco estocástico de series de tiempo basado en <b>Modelos de Factores Dinámicos y Vectores de Corrección de Error (FAVAR-VECM)</b> para analizar, probar vectores de cointegración y pronosticar el impacto de la presión inmobiliaria y gentrificación comercial en el desplazamiento demográfico en la ZMVM a un horizonte de 12 a 20 trimestres.", body_style))
    story.append(Paragraph("<b>Objetivos Específicos:</b> 1) Extraer factores latentes mediante DFM. 2) Evaluar integrabilidad I(d) mediante ADF y KPSS. 3) Probar vectores de cointegración de Johansen. 4) Estimar IRF y FEVD para medir velocidad de choque. 5) Realizar backtesting fuera de muestra (2021-2024) comparando contra ARIMA y VAR.", body_style))

    # 4. REVISIÓN DE LITERATURA
    story.append(Paragraph("4. MARCO TEÓRICO Y LITERATURA ACADÉMICA", h1_style))
    story.append(Paragraph("• <b>Series Ricas en Datos &amp; FAVAR:</b> Stock &amp; Watson (2002, 2016); Bernanke, Boivin &amp; Eliasz (2005).<br/>• <b>Econometría Urbana &amp; Migración:</b> Saiz, A. (2007); Engsted &amp; Bentzen (1997); Guerrieri et al. (2013) (gentrificación endógena).<br/>• <b>Alojamiento Temporal &amp; Rentas:</b> Barron, Kung &amp; Proserpio (2021); Wachsmuth &amp; Weisler (2018).<br/>• <b>Demografía Matemática:</b> CONAPO (2020–2070); Hyndman &amp; Ullah (2007) (series de tiempo demográficas).", body_style))

    # 5. HALLAZGOS EMPÍRICOS PRELIMINARES
    story.append(Paragraph("5. HALLAZGOS EMPÍRICOS PRELIMINARES (INSIDE AIRBNB CDMX)", h1_style))
    story.append(Paragraph("De la inspección de 31,430 propiedades activas descargadas en <code>raw_data/airbnb_cdmx_summary.csv</code>, se observa una marcada hiper-concentración espacial y sustitución habitacional:", body_style))
    
    ab_data = [
        [Paragraph("<b>Alcaldía</b>", ParagraphStyle('TH1', fontName='Helvetica-Bold', fontSize=8, textColor=SECONDARY)),
         Paragraph("<b>Propiedades Activas</b>", ParagraphStyle('TH2', fontName='Helvetica-Bold', fontSize=8, textColor=SECONDARY)),
         Paragraph("<b>% Total CDMX</b>", ParagraphStyle('TH3', fontName='Helvetica-Bold', fontSize=8, textColor=SECONDARY)),
         Paragraph("<b>Precio Promedio (MXN)</b>", ParagraphStyle('TH4', fontName='Helvetica-Bold', fontSize=8, textColor=SECONDARY)),
         Paragraph("<b>Precio Mediano (MXN)</b>", ParagraphStyle('TH5', fontName='Helvetica-Bold', fontSize=8, textColor=SECONDARY))],
        [Paragraph("Cuauhtémoc", body_style), Paragraph("14,449", body_style), Paragraph("45.97%", body_style), Paragraph("$3,219.75", body_style), Paragraph("$1,979.00", body_style)],
        [Paragraph("Miguel Hidalgo", body_style), Paragraph("4,870", body_style), Paragraph("15.49%", body_style), Paragraph("$3,516.80", body_style), Paragraph("$2,211.50", body_style)],
        [Paragraph("Benito Juárez", body_style), Paragraph("3,623", body_style), Paragraph("11.53%", body_style), Paragraph("$2,017.06", body_style), Paragraph("$1,398.00", body_style)],
        [Paragraph("Coyoacán", body_style), Paragraph("2,458", body_style), Paragraph("7.82%", body_style), Paragraph("$2,957.88", body_style), Paragraph("$1,598.00", body_style)],
    ]
    ab_table = Table(ab_data, colWidths=[1.5*inch, 1.3*inch, 1.1*inch, 1.6*inch, 1.5*inch])
    ab_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(ab_table)
    story.append(Spacer(1, 4))
    story.append(Paragraph("<i>Nota: El 66.82% (21,000 unidades) son viviendas/departamentos completos extraídos del mercado residencial permanente.</i>", ParagraphStyle('Note', fontName='Helvetica-Oblique', fontSize=7.5, textColor=colors.HexColor("#5D6D7E"))))

    # 6. ARQUITECTURA DUCKDB
    story.append(Paragraph("6. ARQUITECTURA DE DATOS (DUCKDB 3NF / ESQUEMA ESTRELLA)", h1_style))
    story.append(Paragraph("Se estructuró la base de datos analítica local en <code>processed_data/tesis_zmvm.duckdb</code> mediante tablas dimensionales (<code>dim_alcaldia</code>, <code>dim_tiempo</code> para 80 trimestres 2005Q1-2024Q4) y de hechos (<code>fact_shf_precios</code>, <code>fact_airbnb_metricas</code>, <code>fact_enoe_movilidad</code>, <code>fact_denue_comercio</code>) acopladas en la vista <code>vista_panel_multivariado</code>.", body_style))

    # 7. PRUEBAS DE ROBUSTEZ QA
    story.append(Paragraph("7. PRUEBAS DE ROBUSTEZ Y CALIDAD ESTADÍSTICA (QA)", h1_style))
    story.append(Paragraph("El módulo <code>src/data_quality/validator.py</code> ejecuta: 1) Pruebas de continuidad temporal estricta (80 trimestres). 2) Detección de atípicos por Desviación Absoluta de la Mediana (MAD). 3) Evaluaciones de raíz unitaria ADF y KPSS para determinar orden I(d).", body_style))

    # 8. FORMULACIÓN MATEMÁTICA
    story.append(Paragraph("8. FORMULACIÓN MATEMÁTICA FAVAR-VECM", h1_style))
    story.append(Paragraph("X_t = &Lambda; F_t + e_t &nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp; &Delta;W_t = &Pi; W_{t-1} + &sum;_{i=1}^{p-1} &Gamma;_i &Delta;W_{t-i} + &epsilon;_t", math_style))
    story.append(Paragraph("donde &Hat;F<sub>t</sub> son factores latentes de presión inmobiliaria/comercial, y &Pi; = &alpha;&beta;' captura los $r$ vectores de cointegración de largo plazo.", body_style))

    # 9. DISCUSIÓN DE DUDAS
    story.append(Paragraph("9. DISCUSIÓN DE DUDAS METODOLÓGICAS Y DE DATOS", h1_style))
    story.append(Paragraph("• <b>Alineación de Frecuencias:</b> Filtro de Kalman en Espacio de Estados.<br/>• <b>Cointegración en Alta Dimensión:</b> Engle-Granger de dos pasos para factores o Lasso-VECM.<br/>• <b>Identificación Estructural:</b> Restricciones de signo (<i>sign restrictions</i>).<br/>• <b>No linealidades:</b> Pruebas de Hansen y modelos TVAR.<br/>• <b>Desafíos de Datos:</b> Ajuste del choque de pandemia COVID-19 (2020Q2) en la ENOE.", body_style))

    # 10. EVALUACIÓN Y CRONOGRAMA
    story.append(Paragraph("10. EVALUACIÓN FUERA DE MUESTRA Y CRONOGRAMA (12 MESES)", h1_style))
    story.append(Paragraph("Backtesting fuera de muestra (2021Q1-2024Q4) comparando FAVAR-VECM vs. ARIMA y VAR tradicional con métricas RMSE y MAE. Cronograma de 12 meses divididos en 6 fases operativas.", body_style))

    story.append(Spacer(1, 12))
    sig_data = [
        [Paragraph("____________________________________________<br/><b>Carlos Guillermo Mayorga Tapia</b><br/>Alumno — Maestría en Estadística", ParagraphStyle('Sig1', fontName='Helvetica', fontSize=8, alignment=TA_CENTER)),
         Paragraph("____________________________________________<br/><b>Dr. José Eluid Silva Urrutia</b><br/>Asesor / Director de Tesis", ParagraphStyle('Sig2', fontName='Helvetica', fontSize=8, alignment=TA_CENTER))]
    ]
    sig_table = Table(sig_data, colWidths=[3.5*inch, 3.5*inch])
    story.append(KeepTogether(sig_table))
    
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF extenso generado exitosamente en: {output_path}")

if __name__ == "__main__":
    out_pdf = "/Users/carlosmayorga/github/anahuac/seminario_investigacion/Propuesta_Tesis_Carlos_Mayorga_Anahuac.pdf"
    if len(sys.argv) > 1:
        out_pdf = sys.argv[1]
    create_proposal_pdf(out_pdf)
