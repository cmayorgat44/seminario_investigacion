# 📊 Modelación de Factores Dinámicos y Cointegración (FAVAR-VECM) para el Pronóstico de la Presión Inmobiliaria y el Desplazamiento Demográfico en la ZMVM

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![Conda](https://img.shields.io/badge/Conda-tesis__estadistica-green.svg)](https://docs.conda.io/)
[![DuckDB](https://img.shields.io/badge/Database-DuckDB_3NF-orange.svg)](https://duckdb.org/)
[![Version](https://img.shields.io/badge/Proposal-v3.0_Extensa-brightgreen.svg)](Propuesta_Tesis_Carlos_Mayorga_Anahuac.pdf)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

**Protocolo de Tesis para la Maestría en Estadística (Versión Extensa 3.0)**  
**Universidad Anáhuac México Norte — Facultad de Ciencias Actuariales**

* **Autor:** Carlos Guillermo Mayorga Tapia ([@cmayorgat44](https://github.com/cmayorgat44))
* **Asesor:** Dr. José Eluid Silva Urrutia
* **Contacto:** `mayorgacg@gmail.com`
* **Cobertura Geográfica:** Zona Metropolitana del Valle de México (ZMVM) — 19 alcaldías y municipios clave.
* **Periodo de Análisis:** 2005Q1 – 2024Q4 (80 trimestres continuos).

---

## 📑 Documentos del Protocolo
- 📄 **Documento de Tesis (PDF Extenso Oficial v3.0):** [Propuesta_Tesis_Carlos_Mayorga_Anahuac.pdf](Propuesta_Tesis_Carlos_Mayorga_Anahuac.pdf)
- 📝 **Protocolo Markdown Extenso Completo:** [propuesta_tesis_carlos_mayorga.md](https://github.com/cmayorgat44/seminario_investigacion/blob/main/propuesta_tesis_carlos_mayorga.md) *(v3.0)*
- 💓 **Monitor de Estatus del Proyecto:** [heartbeat.md](heartbeat.md)
- 🕸️ **Grafo de Arquitectura (Graphify):** [docs/architecture_graph.md](docs/architecture_graph.md)

---

## 📌 Resumen Ejecutivo Ampliado

La Zona Metropolitana del Valle de México (ZMVM), con más de 21 millones de habitantes, vive una drástica reestructuración urbana. Sectores centrales experimentan una marcada gentrificación comercial y una rápida expansión del alquiler vacacional de corta estancia (plataformas digitales como Airbnb).

Las proyecciones demográficas tradicionales en México —lideradas por el Consejo Nacional de Población (CONAPO)— utilizan el **Método de Componentes Demográficos (MCD)** en horizontes decenales a escala estatal o nacional. Aunque el MCD es el estándar oficial para la planeación gubernamental, opera bajo un marco **determinista** incapaz de capturar choques socioeconómicos urbanos de alta frecuencia (trimestrales) y la incertidumbre estocástica asociada a la movilidad laboral y el desplazamiento poblacional secundario.

Este proyecto propone abordar el desplazamiento demográfico urbano mediante un modelo de **Series de Tiempo de Alta Dimensión** basado en **Factores Dinámicos Aumentados en Vectores Autorregresivos con Corrección de Error (FAVAR-VECM)**. El objetivo central es integrar indicadores inmobiliarios (SHF), actividad comercial (DENUE), alojamiento vacacional (Airbnb) y microdatos de empleo y migración (ENOE) para cuantificar la velocidad de transmisión de los choques inmobiliarios y predecir el desplazamiento a un horizonte de 3 a 5 años (12–20 trimestres).

---

## 🔬 Hipótesis e Investigación

* **Hipótesis Principal ($H_1$):** La presión de precios de vivienda (Índice SHF) y la densidad de servicios comerciales gentrificadores / rentas cortas (DENUE/Airbnb) mantienen una relación de cointegración estocástica de largo plazo con la tasa de saldo migratorio neto negativo de la población trabajadora en las alcaldías centrales de la ZMVM.
* **Hipótesis Secundaria 1 ($H_2$):** La reducción de dimensionalidad mediante un Modelo de Factores Dinámicos (DFM) extrae factores latentes de *Presión Inmobiliaria* ($\hat{F}_{1,t}$) y *Gentrificación Comercial* ($\hat{F}_{2,t}$) que reducen el error cuadrático medio de pronóstico fuera de muestra (RMSE) frente a modelos ARIMA y VAR tradicionales.
* **Hipótesis Secundaria 2 ($H_3$):** Los choques inmobiliarios presentan una respuesta asimétrica en el desplazamiento poblacional (medida vía Funciones de Impulso-Respuesta, IRF), alcanzando su mayor impacto entre el cuarto y el octavo trimestre posterior al choque.

---

## 🧮 Formulación Matemática del Modelo FAVAR-VECM

Sea $X_t$ ($N \times 1$) el vector de series observadas urbanas, descompuesto mediante un Modelo de Factores Dinámicos (DFM):

$$X_t = \Lambda F_t + e_t , \quad e_t \sim \mathcal{N}(0, \Omega)$$

El vector aumentado $W_t = [\hat{F}_t', Y_t']'$ (donde $Y_t$ contiene los saldos migratorios y salarios de la ENOE) se especifica como un Modelo de Corrección de Error Vectorial (VECM):

$$\Delta W_t = \Pi W_{t-1} + \sum_{i=1}^{p-1} \Gamma_i \Delta W_{t-i} + \varepsilon_t , \quad \varepsilon_t \sim \text{WN}(0, \Sigma)$$

donde $\Pi = \alpha \beta'$ representa la matriz de rango $r$ que rige las relaciones de cointegración a largo plazo.

---

## 📈 Hallazgos Empíricos (Dataset Inside Airbnb CDMX)

De la inspección de **31,430 propiedades activas** descargadas en `raw_data/airbnb_cdmx_summary.csv`:

| Alcaldía | Propiedades Activas | % Total CDMX | Precio Promedio (MXN) | Precio Mediano (MXN) |
| :--- | :---: | :---: | :---: | :---: |
| **Cuauhtémoc** | **14,449** | **45.97%** | **$3,219.75** | **$1,979.00** |
| **Miguel Hidalgo** | **4,870** | **15.49%** | **$3,516.80** | **$2,211.50** |
| **Benito Juárez** | **3,623** | **11.53%** | **$2,017.06** | **$1,398.00** |
| **Coyoacán** | **2,458** | **7.82%** | **$2,957.88** | **$1,598.00** |

*El 66.82% (21,000 propiedades) son departamentos/casas completas extraídas del mercado residencial permanente.*

---

## 🏗️ Arquitectura de Software y Datos (DuckDB 3NF)

```
seminario_investigacion/
├── raw_data/                       # Datos crudos
│   └── airbnb_cdmx_summary.csv
├── processed_data/                 # Base de datos relacional
│   ├── tesis_zmvm.duckdb           # DuckDB analítica local (3NF / Esquema Estrella)
│   └── resumen_airbnb_por_alcaldia.csv
├── src/                            # Módulos principales
│   ├── database/
│   │   └── schema.py               # Esquema relacional en DuckDB
│   └── data_quality/
│       └── validator.py            # Suite QA (outliers MAD, ADF, KPSS)
├── scripts/                        # Scripts ejecutables
│   ├── inicializar_base_datos.py
│   ├── analizar_airbnb_cdmx.py
│   ├── diagnosticar_fuentes_datos.py
│   └── generar_grafo_proyecto.py
├── docs/
│   └── architecture_graph.md       # Diagrama en Mermaid
├── environment.yml                 # Entorno conda reproducible
├── generar_pdf_propuesta.py        # Generador del PDF extenso v3.0
├── Propuesta_Tesis_Carlos_Mayorga_Anahuac.pdf # PDF Oficial v3.0
├── heartbeat.md                    # Monitor del proyecto
└── README.md                       # Documentación principal
```

---

## ⚡ Guía de Instalación y Ejecución

```bash
# 1. Clonar el repositorio
git clone git@personal.github.com:cmayorgat44/seminario_investigacion.git
cd seminario_investigacion

# 2. Activar el ambiente de Conda
conda env create -f environment.yml
conda activate tesis_estadistica

# 3. Inicializar DuckDB y ejecutar pruebas de QA
python scripts/inicializar_base_datos.py

# 4. Generar el PDF y el Grafo de Arquitectura
python scripts/generar_grafo_proyecto.py
python generar_pdf_propuesta.py
```

---

## 📜 Licencia y Contacto
* **Autor:** Carlos Guillermo Mayorga Tapia  
* **Asesor:** Dr. José Eluid Silva Urrutia  
* **Institución:** Universidad Anáhuac México Norte — Maestría en Estadística  
* **Contacto:** `mayorgacg@gmail.com`
