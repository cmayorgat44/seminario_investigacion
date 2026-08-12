# Reglas de Agente para el Proyecto de Tesis

Estas reglas rigen el comportamiento de los agentes que trabajan en este repositorio.

## ❄️ Freeze de Código y Estructura (Agosto 2026)

Se ha decretado un **freeze de código** para todos los componentes e infraestructura base construidos hasta el 11 de agosto de 2026.

### Archivos Congelados (NO Modificar)
Los siguientes archivos no deben ser modificados bajo ninguna circunstancia, a menos que el usuario lo solicite de manera explícita y directa:
- [Propuesta_Tesis_Carlos_Mayorga_Anahuac.pdf](file:///Users/carlosmayorga/github/anahuac/seminario_investigacion/Propuesta_Tesis_Carlos_Mayorga_Anahuac.pdf) (Propuesta formal de tesis en PDF)
- [generar_pdf_propuesta.py](file:///Users/carlosmayorga/github/anahuac/seminario_investigacion/generar_pdf_propuesta.py) (Script de generación del PDF de la propuesta)
- [heartbeat.md](file:///Users/carlosmayorga/github/anahuac/seminario_investigacion/heartbeat.md) (Estado y avance de control del proyecto a esta fecha)
- [src/database/schema.py](file:///Users/carlosmayorga/github/anahuac/seminario_investigacion/src/database/schema.py) (Estructura relacional DuckDB 3NF)
- [src/data_quality/validator.py](file:///Users/carlosmayorga/github/anahuac/seminario_investigacion/src/data_quality/validator.py) (Suite de validación QA estadística)
- [docs/architecture_graph.md](file:///Users/carlosmayorga/github/anahuac/seminario_investigacion/docs/architecture_graph.md) (Diagrama de arquitectura del proyecto)
- [environment.yml](file:///Users/carlosmayorga/github/anahuac/seminario_investigacion/environment.yml) (Configuración del ambiente Conda `tesis_estadistica`)
- Todos los scripts auxiliares en `scripts/` creados hasta el momento:
  - [scripts/analizar_airbnb_cdmx.py](file:///Users/carlosmayorga/github/anahuac/seminario_investigacion/scripts/analizar_airbnb_cdmx.py)
  - [scripts/descargar_muestra_airbnb.py](file:///Users/carlosmayorga/github/anahuac/seminario_investigacion/scripts/descargar_muestra_airbnb.py)
  - [scripts/diagnosticar_fuentes_datos.py](file:///Users/carlosmayorga/github/anahuac/seminario_investigacion/scripts/diagnosticar_fuentes_datos.py)
  - [scripts/generar_grafo_proyecto.py](file:///Users/carlosmayorga/github/anahuac/seminario_investigacion/scripts/generar_grafo_proyecto.py)
  - [scripts/inicializar_base_datos.py](file:///Users/carlosmayorga/github/anahuac/seminario_investigacion/scripts/inicializar_base_datos.py)

### Lineamientos de Extensión
1. **Nuevos Módulos**: Cualquier nueva funcionalidad (por ejemplo, extractores de datos SHF, extractores de ENOE, modelos de cointegración, etc.) debe desarrollarse en archivos nuevos dentro de `src/` o `scripts/` correspondientes.
2. **Preservar el Esquema**: El esquema relacional existente en [schema.py](file:///Users/carlosmayorga/github/anahuac/seminario_investigacion/src/database/schema.py) es definitivo para la fase actual. No se deben añadir, renombrar o eliminar tablas o columnas sin aprobación previa explícita del usuario.
3. **Integridad de Datos**: Los pipelines y flujos de datos deben consumir la base de datos DuckDB tal y como está definida en el esquema de hoy.
