# 🕸️ Grafo de Arquitectura del Proyecto (Graphify)
## Maestría en Estadística — Universidad Anáhuac México Norte

Este documento mapea las relaciones de dependencia entre fuentes de datos, módulos de código, base de datos analítica y salidas del proyecto.

### Diagrama de Grafo de Flujo

```mermaid
graph TD
    Data__SHF_Vivienda["Data: SHF (Vivienda)"] --> DuckDB__tesis_zmvm_duckdb["DuckDB: tesis_zmvm.duckdb"]
    Data__ENOE_Empleo_Migración["Data: ENOE (Empleo/Migración)"] --> DuckDB__tesis_zmvm_duckdb["DuckDB: tesis_zmvm.duckdb"]
    Data__DENUE_Comercio["Data: DENUE (Comercio)"] --> DuckDB__tesis_zmvm_duckdb["DuckDB: tesis_zmvm.duckdb"]
    Data__Inside_Airbnb["Data: Inside Airbnb"] --> Script__scripts_analizar_airbnb_cdmx_py["Script: scripts/analizar_airbnb_cdmx.py"]
    DuckDB__tesis_zmvm_duckdb["DuckDB: tesis_zmvm.duckdb"] --> QA_Validator__src_data_quality_validator_py["QA Validator: src/data_quality/validator.py"]
    Schema__src_database_schema_py["Schema: src/database/schema.py"] --> DuckDB__tesis_zmvm_duckdb["DuckDB: tesis_zmvm.duckdb"]
    Script__scripts_inicializar_base_datos_py["Script: scripts/inicializar_base_datos.py"] --> Schema__src_database_schema_py["Schema: src/database/schema.py"]
    Script__scripts_inicializar_base_datos_py["Script: scripts/inicializar_base_datos.py"] --> QA_Validator__src_data_quality_validator_py["QA Validator: src/data_quality/validator.py"]
    Script__scripts_analizar_airbnb_cdmx_py["Script: scripts/analizar_airbnb_cdmx.py"] --> DuckDB__tesis_zmvm_duckdb["DuckDB: tesis_zmvm.duckdb"]
    generar_pdf_propuesta_py["generar_pdf_propuesta.py"] --> Doc__Propuesta_Tesis_Carlos_Mayorga_Anahuac_pdf["Doc: Propuesta_Tesis_Carlos_Mayorga_Anahuac.pdf"]
```

### Resumen de Nodos de la Arquitectura
* **Fuentes de Datos (Sources):** SHF, ENOE, DENUE, Inside Airbnb CDMX.
* **Capa de Almacenamiento:** DuckDB (`processed_data/tesis_zmvm.duckdb`).
* **Módulos de Código:** `src/database/schema.py`, `src/data_quality/validator.py`.
* **Entregables Principales:** `Propuesta_Tesis_Carlos_Mayorga_Anahuac.pdf`, `heartbeat.md`.
