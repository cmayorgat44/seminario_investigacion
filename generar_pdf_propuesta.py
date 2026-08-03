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
        
        # Don't draw headers/footers on page 1 (cover-like header)
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
    
    # Palette
    PRIMARY = colors.HexColor("#D35400")   # Anahuac Orange Accent
    SECONDARY = colors.HexColor("#2C3E50") # Deep Slate Navy
    TEXT_DARK = colors.HexColor("#2B2B2B") # Off-black body
    BG_LIGHT = colors.HexColor("#F8F9F9")  # Soft background
    BORDER_COLOR = colors.HexColor("#E5E7E9")
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=SECONDARY,
        alignment=TA_CENTER,
        spaceAfter=10
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=PRIMARY,
        alignment=TA_CENTER,
        spaceAfter=15
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=SECONDARY,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=PRIMARY,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=TEXT_DARK,
        alignment=TA_JUSTIFY,
        spaceAfter=6
    )
    
    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=15,
        bulletIndent=5,
        spaceAfter=4
    )
    
    math_style = ParagraphStyle(
        'Math_Custom',
        parent=styles['Normal'],
        fontName='Courier-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1A5276"),
        alignment=TA_CENTER,
        spaceBefore=6,
        spaceAfter=6
    )
    
    meta_label = ParagraphStyle('MetaLabel', fontName='Helvetica-Bold', fontSize=9.5, leading=13, textColor=SECONDARY)
    meta_val = ParagraphStyle('MetaVal', fontName='Helvetica', fontSize=9.5, leading=13, textColor=TEXT_DARK)
    
    story = []
    
    # --- HEADER BLOCK (UNIVERSIDAD ANÁHUAC) ---
    story.append(Paragraph("UNIVERSIDAD ANÁHUAC MÉXICO", ParagraphStyle('UniHeader', fontName='Helvetica-Bold', fontSize=14, leading=17, textColor=PRIMARY, alignment=TA_CENTER)))
    story.append(Paragraph("Facultad de Ciencias Actuariales &nbsp;|&nbsp; Posgrado en Estadística", ParagraphStyle('SubHeader', fontName='Helvetica', fontSize=10, leading=13, textColor=SECONDARY, alignment=TA_CENTER)))
    story.append(Paragraph("Maestría en Estadística — Seminario de Investigación", ParagraphStyle('ProgHeader', fontName='Helvetica-Oblique', fontSize=9.5, leading=12, textColor=colors.HexColor("#5D6D7E"), alignment=TA_CENTER)))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceBefore=0, spaceAfter=15))
    
    # --- TITLE ---
    story.append(Paragraph("PROPUESTA DE PROTOCOLO DE TESIS", title_style))
    story.append(Paragraph("Modelación de Factores Dinámicos y Cointegración (FAVAR-VECM) para el Pronóstico de la Presión Inmobiliaria y el Desplazamiento Demográfico en la ZMVM", subtitle_style))
    
    # --- METADATA BOX ---
    meta_data = [
        [Paragraph("<b>Alumno:</b>", meta_label), Paragraph("Carlos Guillermo Mayorga Tapia", meta_val),
         Paragraph("<b>Asesor Propuesto:</b>", meta_label), Paragraph("Dr. José Eluid Silva Urrutia", meta_val)],
        [Paragraph("<b>Programa:</b>", meta_label), Paragraph("Maestría en Estadística", meta_val),
         Paragraph("<b>Fecha:</b>", meta_label), Paragraph("Agosto de 2026", meta_val)],
        [Paragraph("<b>Área:</b>", meta_label), Paragraph("Series de Tiempo &amp; Demografía Cuantitativa", meta_val),
         Paragraph("<b>Cobertura:</b>", meta_label), Paragraph("Zona Metropolitana del Valle de México (ZMVM)", meta_val)]
    ]
    meta_table = Table(meta_data, colWidths=[1.1*inch, 2.4*inch, 1.3*inch, 2.2*inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))
    
    # --- SECTIONS ---
    
    # 1. INTRODUCCIÓN Y CONTEXTO
    story.append(Paragraph("1. INTRODUCCIÓN Y CONTEXTO", h1_style))
    story.append(Paragraph(
        "La Zona Metropolitana del Valle de México (ZMVM), con una población superior a los 21 millones de habitantes, atraviesa una profunda reestructuración sociodemográfica. En las últimas dos décadas, sectores centrales y peri-centrales de la metrópoli han experimentado acelerados procesos de apreciación del suelo, gentrificación comercial y una fuerte expansión del alquiler vacacional de corta estancia mediado por plataformas digitales (ej. Airbnb).",
        body_style
    ))
    story.append(Paragraph(
        "A nivel de planificación nacional, las proyecciones demográficas han dependido tradicionalmente del Método de Componentes Demográficos (MCD) del Consejo Nacional de Población (CONAPO). Sin embargo, el MCD opera bajo un marco determinista en horizontes decenales a escala nacional o estatal. Este enfoque resulta insuficiente para capturar choques socioeconómicos urbanos de alta frecuencia (trimestrales o anuales) y su consecuente impacto en la movilidad y el desplazamiento secundario de la fuerza laboral hacia las periferias urbanas.",
        body_style
    ))
    story.append(Paragraph(
        "Esta propuesta aborda el desplazamiento poblacional desde un marco riguroso de <b>Series de Tiempo de Alta Dimensión</b>. Se plantea integrar indicadores económicos e inmobiliarios de alta frecuencia con microdatos de empleo y movilidad migratoria para probar hipótesis estocásticas de cointegración y pronosticar la dinámica expulsiva y de reacomodo en la ZMVM.",
        body_style
    ))
    
    # 2. PLANTEAMIENTO DEL PROBLEMA Y JUSTIFICACIÓN
    story.append(Paragraph("2. PLANTEAMIENTO DEL PROBLEMA Y JUSTIFICACIÓN", h1_style))
    story.append(Paragraph(
        "Existe una brecha metodológica sustancial en la literatura nacional: los censos de población (decenales) no ofrecen la resolución temporal requerida para guiar políticas públicas continuas, mientras que los índices inmobiliarios de alta frecuencia raramente se conectan estadísticamente con los flujos de fuerza laboral.",
        body_style
    ))
    story.append(Paragraph(
        "El desafío estadístico central reside en la dimensionalidad (<i>p &gt;&gt; n</i>) y en la naturaleza estocástica no estacionaria de las series. Al integrar decenas de categorías comerciales (DENUE-INEGI), métricas de plataformas de alojamiento e índices de precios habitacionales (SHF) junto con variables de la Encuesta Nacional de Ocupación y Empleo (ENOE), se obtiene un entorno de alta dimensión donde los modelos VAR tradicionales sufren de sobreajuste y agotamiento de grados de libertad.",
        body_style
    ))
    story.append(Paragraph(
        "Para resolver esta limitación, la investigación adopta un modelo de <b>Factores Dinámicos Aumentados en Vectores Autorregresivos con Corrección de Error (FAVAR-VECM)</b>. Este enfoque reduce el entorno 'rico en datos' (<i>data-rich environment</i>) a un conjunto parsimonioso de factores latentes, preservando las relaciones de equilibrio a largo plazo y la dinámica de corto plazo.",
        body_style
    ))
    
    # 3. OBJETIVOS
    story.append(Paragraph("3. OBJETIVOS DE INVESTIGACIÓN", h1_style))
    story.append(Paragraph("<b>Objetivo General:</b>", h2_style))
    story.append(Paragraph(
        "Desarrollar, estimar y evaluar un marco estocástico de series de tiempo basado en <b>Modelos de Factores Dinámicos y Vectores de Corrección de Error (FAVAR-VECM)</b> para analizar, probar vectores de cointegración y pronosticar el impacto de la presión inmobiliaria y la gentrificación comercial sobre el desplazamiento demográfico en la ZMVM a un horizonte de 12 a 20 trimestres.",
        body_style
    ))
    story.append(Paragraph("<b>Objetivos Específicos:</b>", h2_style))
    story.append(Paragraph("• <b>Extracción de Factores Latentes:</b> Construir un Modelo de Factores Dinámicos (DFM) que reduzca la dimensionalidad del DENUE, Índice SHF e Inside Airbnb en factores de <i>Presión Inmobiliaria</i> y <i>Gentrificación Comercial</i>.", bullet_style))
    story.append(Paragraph("• <b>Evaluación de Integrabilidad:</b> Verificar la estacionariedad y orden de integración <i>I(d)</i> de las series mediante pruebas ADF, Phillips-Perron y KPSS.", bullet_style))
    story.append(Paragraph("• <b>Prueba y Modelación de Cointegración:</b> Evaluar la existencia de vectores de cointegración (Johansen rank test) entre los factores latentes urbanos y los saldos de movilidad laboral de la ENOE.", bullet_style))
    story.append(Paragraph("• <b>Análisis Dinámico de Inferencia:</b> Estimar Funciones de Impulso-Respuesta (IRF) y Descomposición de Varianza de Error de Pronóstico (FEVD) para cuantificar la velocidad de transmisión de los choques inmobiliarios.", bullet_style))
    story.append(Paragraph("• <b>Validación Fuera de Muestra:</b> Evaluar la precisión predictiva del FAVAR-VECM contra modelos benchmark univariados (ARIMA) y VAR mediante ventanas móviles (<i>rolling windows</i>) y métricas RMSE/MAE.", bullet_style))
    
    # 4. MARCO TEÓRICO Y LITERATURA ACADÉMICA
    story.append(Paragraph("4. MARCO TEÓRICO Y REVISIÓN DE LA LITERATURA", h1_style))
    story.append(Paragraph(
        "La investigación se fundamenta en tres vertientes principales de la literatura econométrica y demográfica internacional y nacional:",
        body_style
    ))
    
    lit_data = [
        [Paragraph("<b>Vertiente Literaria</b>", ParagraphStyle('TH1', fontName='Helvetica-Bold', fontSize=9, textColor=SECONDARY)),
         Paragraph("<b>Autores Clave &amp; Referencias</b>", ParagraphStyle('TH2', fontName='Helvetica-Bold', fontSize=9, textColor=SECONDARY)),
         Paragraph("<b>Aporte Metodológico</b>", ParagraphStyle('TH3', fontName='Helvetica-Bold', fontSize=9, textColor=SECONDARY))],
        
        [Paragraph("Series Ricas en Datos &amp; FAVAR", body_style),
         Paragraph("Stock &amp; Watson (2002, 2016)<br/>Bernanke, Boivin &amp; Eliasz (2005)", body_style),
         Paragraph("Extracción de factores latentes dinámicos vía componentes principales en entornos <i>p &gt;&gt; n</i> sin agotar grados de libertad.", body_style)],
        
        [Paragraph("Econometría Urbana &amp; Vivienda", body_style),
         Paragraph("Saiz, A. (2007)<br/>Engsted &amp; Bentzen (1997)<br/>Guerrieri et al. (2013)", body_style),
         Paragraph("Cointegración entre shocks de oferta/demanda habitacional, incrementos de renta y dinámicas de gentrificación endógena.", body_style)],
        
        [Paragraph("Alojamiento Temporal &amp; Renta", body_style),
         Paragraph("Barron, Kung &amp; Proserpio (2021)", body_style),
         Paragraph("Inferencia causal del impacto de plataformas (Airbnb) sobre la conversión de vivienda residencial y expulsión de inquilinos.", body_style)],
        
        [Paragraph("Demografía Matemática en México", body_style),
         Paragraph("CONAPO (2020-2070)<br/>Hyndman &amp; Ullah (2007)", body_style),
         Paragraph("Transición del enfoque determinista de componentes hacia métodos estocásticos y de datos funcionales en demografía.", body_style)]
    ]
    lit_table = Table(lit_data, colWidths=[1.8*inch, 2.2*inch, 3.0*inch])
    lit_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(lit_table)
    story.append(Spacer(1, 10))
    
    # 5. FUENTES DE DATOS ABIERTOS
    story.append(Paragraph("5. FUENTES DE DATOS ABIERTOS Y FRECUENCIA TEMPORAL", h1_style))
    story.append(Paragraph(
        "Se utilizarán exclusivamente fuentes públicas abiertas del Estado mexicano e instituciones internacionales:",
        body_style
    ))
    
    ds_data = [
        [Paragraph("<b>Fuente</b>", ParagraphStyle('TH1', fontName='Helvetica-Bold', fontSize=9, textColor=SECONDARY)),
         Paragraph("<b>Frecuencia</b>", ParagraphStyle('TH2', fontName='Helvetica-Bold', fontSize=9, textColor=SECONDARY)),
         Paragraph("<b>Periodo</b>", ParagraphStyle('TH3', fontName='Helvetica-Bold', fontSize=9, textColor=SECONDARY)),
         Paragraph("<b>Variables de Interés</b>", ParagraphStyle('TH4', fontName='Helvetica-Bold', fontSize=9, textColor=SECONDARY))],
        
        [Paragraph("<b>Índice SHF</b> (Sociedad Hipotecaria Federal)", body_style), Paragraph("Trimestral", body_style), Paragraph("2005 – 2024<br/>(80 obs.)", body_style), Paragraph("Índice de precios de vivienda ajustado por inflación en ZMVM y por alcaldía.", body_style)],
        [Paragraph("<b>INEGI – ENOE</b> (Encuesta Ocupación y Empleo)", body_style), Paragraph("Trimestral", body_style), Paragraph("2005 – 2024", body_style), Paragraph("Microdatos de cambio de residencia, salarios, informalidad y saldo migratorio laboral.", body_style)],
        [Paragraph("<b>INEGI – DENUE</b> (Directorio Unidades Econ.)", body_style), Paragraph("Semestral / Anual", body_style), Paragraph("2010 – 2024", body_style), Paragraph("Conteo y densidad de establecimientos comerciales de sustitución gentrificadora.", body_style)],
        [Paragraph("<b>Inside Airbnb / CDMX Datos Abiertos</b>", body_style), Paragraph("Mensual / Trimestral", body_style), Paragraph("2015 – 2024", body_style), Paragraph("Listados activos, tarifa media diaria (ADR) y tasa de ocupación estimada.", body_style)]
    ]
    ds_table = Table(ds_data, colWidths=[1.8*inch, 1.0*inch, 1.2*inch, 3.0*inch])
    ds_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(ds_table)
    story.append(Spacer(1, 10))
    
    # 6. FORMULACIÓN MATEMÁTICA
    story.append(Paragraph("6. FORMULACIÓN MATEMÁTICA DEL MODELO FAVAR-VECM", h1_style))
    story.append(Paragraph(
        "Sea <i>X<sub>t</sub></i> un vector <i>N &times; 1</i> de series de tiempo socioeconómicas observadas en el trimestre <i>t = 1, ..., T</i>, donde <i>N</i> representa la dimensión expandida de indicadores urbanos.",
        body_style
    ))
    story.append(Paragraph("<b>Paso 1: Modelo de Factores Dinámicos (DFM)</b>", h2_style))
    story.append(Paragraph(
        "El vector observacional <i>X<sub>t</sub></i> se descompone en <i>K &lt;&lt; N</i> factores latentes <i>F<sub>t</sub></i> y un componente idiosincrásico <i>e<sub>t</sub></i>:",
        body_style
    ))
    story.append(Paragraph("X_t = &Lambda; F_t + e_t , &nbsp;&nbsp;&nbsp;&nbsp; e_t ~ N(0, &Omega;)", math_style))
    story.append(Paragraph(
        "donde &Lambda; es la matriz de cargas factoriales (<i>N &times; K</i>). Los factores &Hat;F<sub>t</sub> son estimados vía Componentes Principales Dinámicos o Filtro de Kalman en Espacio de Estados.",
        body_style
    ))
    story.append(Paragraph("<b>Paso 2: Sistema FAVAR-VECM Cointegrado</b>", h2_style))
    story.append(Paragraph(
        "Definimos el vector observado de variables sociodemográficas clave <i>Y<sub>t</sub></i> (ej. Saldo migratorio e ingreso laboral de la ENOE). Construimos el vector aumentado <i>W<sub>t</sub> = [&Hat;F<sub>t</sub>', Y<sub>t</sub>']'</i>.",
        body_style
    ))
    story.append(Paragraph(
        "Si las componentes de <i>W<sub>t</sub></i> son <i>I(1)</i> y existe una relación de cointegración con rango <i>r &gt; 0</i>, el modelo adopta la representación VECM:",
        body_style
    ))
    story.append(Paragraph("&Delta;W_t = &Pi; W_{t-1} + &sum;_{i=1}^{p-1} &Gamma;_i &Delta;W_{t-i} + &epsilon;_t , &nbsp;&nbsp;&nbsp;&nbsp; &epsilon;_t ~ WN(0, &Sigma;)", math_style))
    story.append(Paragraph(
        "donde <b>&Pi; = &alpha;&beta;'</b> es la matriz de rango <i>r</i> (con &beta; conteniendo los vectores de cointegración de largo plazo y &alpha; las velocidades de ajuste) y &Gamma;<sub>i</sub> gobierna la dinámica de corto plazo.",
        body_style
    ))
    
    # 7. DISCUSIÓN DE DUDAS METODOLÓGICAS
    story.append(Paragraph("7. DUDAS Y RETOS METODOLÓGICOS PROPUESTOS PARA DISCUSIÓN", h1_style))
    story.append(Paragraph(
        "A fin de enriquecer la discusión en el Seminario de Investigación, se sintetizan cuatro cuestiones metodológicas centrales a tratar con el Dr. Silva Urrutia:",
        body_style
    ))
    story.append(Paragraph("1. <b>Alineación de Frecuencias Dispares (Temporal Aggregation &amp; State-Space):</b>", h2_style))
    story.append(Paragraph(
        "<i>Desafío:</i> SHF y ENOE son trimestrales, DENUE es semestral/anual y Airbnb es mensual.<br/>"
        "<i>Estrategia de Mitigación:</i> Formular un modelo de Espacio de Estados acoplado al Filtro de Kalman para imputar y agregar temporalmente las series de menor frecuencia a una malla trimestral sin distorsionar la estructura autorregresiva.",
        body_style
    ))
    story.append(Paragraph("2. <b>Estimación del Rango de Cointegración en Entornos de Alta Dimensión:</b>", h2_style))
    story.append(Paragraph(
        "<i>Desafío:</i> La prueba de Johansen puede perder potencia si los factores latentes estimados contienen error muestral de primera etapa.<br/>"
        "<i>Estrategia de Mitigación:</i> Aplicar la prueba de cointegración en dos pasos de Engle-Granger para modelos de factores o implementar regularización Lasso en la matriz de corrección de error (Lasso-VECM).",
        body_style
    ))
    story.append(Paragraph("3. <b>Identificación Estructural de los Choques en el FAVAR:</b>", h2_style))
    story.append(Paragraph(
        "<i>Desafío:</i> La descomposición de Cholesky tradicional exige imponer un ordenamiento estricto recursivo entre gentrificación y desplazamiento demográfico.<br/>"
        "<i>Estrategia de Mitigación:</i> Evaluar la implementación de restricciones de signo (<i>sign restrictions</i>) en la matriz estructural <b>B</b><sub>0</sub> basadas en teoría económica urbana.",
        body_style
    ))
    story.append(Paragraph("4. <b>Linealidad vs. Regímenes de Umbral (TVAR):</b>", h2_style))
    story.append(Paragraph(
        "<i>Desafío:</i> El desplazamiento poblacional podría responder de forma no lineal ante choques inmobiliarios extremos.<br/>"
        "<i>Estrategia de Mitigación:</i> Aplicar la prueba de linealidad de Hansen; de ser rechazada, extender hacia un Modelo Vectorial Autorregresivo de Umbral (TVAR).",
        body_style
    ))
    
    # 8. DUDAS SOBRE LAS FUENTES DE DATOS
    story.append(Paragraph("8. DUDAS Y RETOS SOBRE LAS FUENTES DE DATOS", h1_style))
    story.append(Paragraph("• <b>Heterogeneidad Espacial del DENUE:</b> El DENUE captura establecimientos formales, pero presenta rezagos en altas/bajas de micro-negocios. <i>Mitigación:</i> Construir un índice relativo por código SCIAN centrado en comercios gentrificadores.", bullet_style))
    story.append(Paragraph("• <b>Cobertra Periférica de Airbnb:</b> Alta penetración en alcaldías centrales (Cuauhtémoc, Miguel Hidalgo), pero menor en municipios conurbados del Edomex. <i>Mitigación:</i> Introducir una matriz de contigüidad espacial <i>W</i> para capturar efectos de desbordamiento (<i>spatial spillovers</i>).", bullet_style))
    story.append(Paragraph("• <b>Discontinuidad por COVID-19 en ENOE (2020Q2):</b> La sustitución temporal por la ETOE creó una brecha muestral. <i>Mitigación:</i> Incluir dummies de intervención o suavizado mediante espacio de estados en 2020.", bullet_style))
    
    # 9. CRONOGRAMA
    story.append(Paragraph("9. CRONOGRAMA PROPUESTO DE TRABAJO (12 MESES)", h1_style))
    
    cron_data = [
        [Paragraph("<b>Fase</b>", ParagraphStyle('TH1', fontName='Helvetica-Bold', fontSize=9, textColor=SECONDARY)),
         Paragraph("<b>Periodo</b>", ParagraphStyle('TH2', fontName='Helvetica-Bold', fontSize=9, textColor=SECONDARY)),
         Paragraph("<b>Entregable &amp; Actividades Clave</b>", ParagraphStyle('TH3', fontName='Helvetica-Bold', fontSize=9, textColor=SECONDARY))],
        
        [Paragraph("Fase I", body_style), Paragraph("Meses 1 – 2", body_style), Paragraph("Extracción, limpieza y armonización de series SHF, ENOE, DENUE y Airbnb a malla trimestral.", body_style)],
        [Paragraph("Fase II", body_style), Paragraph("Meses 3 – 4", body_style), Paragraph("Pruebas de integrabilidad (ADF, KPSS) y estimación del Modelo de Factores Dinámicos (DFM).", body_style)],
        [Paragraph("Fase III", body_style), Paragraph("Meses 5 – 6", body_style), Paragraph("Pruebas de Cointegración de Johansen y especificación del sistema FAVAR-VECM.", body_style)],
        [Paragraph("Fase IV", body_style), Paragraph("Meses 7 – 8", body_style), Paragraph("Estimación de IRF, Descomposición de Varianza (FEVD) y pruebas de causalidad de Granger.", body_style)],
        [Paragraph("Fase V", body_style), Paragraph("Meses 9 – 10", body_style), Paragraph("Validación fuera de muestra (Backtesting 2021-2024) y evaluación contra modelos benchmark.", body_style)],
        [Paragraph("Fase VI", body_style), Paragraph("Meses 11 – 12", body_style), Paragraph("Redacción final del documento de tesis, artículo científico derivado y preparación de la defensa.", body_style)]
    ]
    cron_table = Table(cron_data, colWidths=[1.0*inch, 1.3*inch, 4.7*inch])
    cron_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(cron_table)
    story.append(Spacer(1, 20))
    
    # SIGNATURE BLOCK
    sig_data = [
        [Paragraph("____________________________________________<br/><b>Carlos Guillermo Mayorga Tapia</b><br/>Alumno — Maestría en Estadística", ParagraphStyle('Sig1', fontName='Helvetica', fontSize=9, alignment=TA_CENTER)),
         Paragraph("____________________________________________<br/><b>Dr. José Eluid Silva Urrutia</b><br/>Asesor / Director de Tesis", ParagraphStyle('Sig2', fontName='Helvetica', fontSize=9, alignment=TA_CENTER))]
    ]
    sig_table = Table(sig_data, colWidths=[3.5*inch, 3.5*inch])
    story.append(KeepTogether(sig_table))
    
    # BUILD PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF generado exitosamente en: {output_path}")

if __name__ == "__main__":
    out_pdf = "/Users/carlosmayorga/github/anahuac/seminario_investigacion/Propuesta_Tesis_Carlos_Mayorga_Anahuac.pdf"
    if len(sys.argv) > 1:
        out_pdf = sys.argv[1]
    create_proposal_pdf(out_pdf)
