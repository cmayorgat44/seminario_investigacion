import os
import sys
import networkx as nx

def generate_graph():
    print("="*70)
    print("  GENERACIÓN DEL GRAFO DE ARQUITECTURA DEL PROYECTO (GRAPHIFY)")
    print("="*70)
    
    os.makedirs("docs", exist_ok=True)
    
    G = nx.DiGraph()
    
    # Nodos de Datos / Fuentes
    G.add_node("Data: SHF (Vivienda)", type="source")
    G.add_node("Data: ENOE (Empleo/Migración)", type="source")
    G.add_node("Data: DENUE (Comercio)", type="source")
    G.add_node("Data: Inside Airbnb", type="source")
    
    # Nodos de Infraestructura & Almacenamiento
    G.add_node("DuckDB: tesis_zmvm.duckdb", type="database")
    G.add_node("Schema: src/database/schema.py", type="code")
    G.add_node("QA Validator: src/data_quality/validator.py", type="code")
    
    # Nodos de Scripts & Ejecutables
    G.add_node("Script: scripts/inicializar_base_datos.py", type="script")
    G.add_node("Script: scripts/analizar_airbnb_cdmx.py", type="script")
    G.add_node("Script: generar_pdf_propuesta.py", type="script")
    
    # Nodos de Salidas / Protocolo
    G.add_node("Doc: Propuesta_Tesis_Carlos_Mayorga_Anahuac.pdf", type="output")
    G.add_node("Doc: heartbeat.md", type="output")
    
    # Aristas (Conexiones de Flujo)
    G.add_edge("Data: Inside Airbnb", "Script: scripts/analizar_airbnb_cdmx.py")
    G.add_edge("Script: scripts/analizar_airbnb_cdmx.py", "DuckDB: tesis_zmvm.duckdb")
    G.add_edge("Schema: src/database/schema.py", "DuckDB: tesis_zmvm.duckdb")
    G.add_edge("Data: SHF (Vivienda)", "DuckDB: tesis_zmvm.duckdb")
    G.add_edge("Data: ENOE (Empleo/Migración)", "DuckDB: tesis_zmvm.duckdb")
    G.add_edge("Data: DENUE (Comercio)", "DuckDB: tesis_zmvm.duckdb")
    G.add_edge("DuckDB: tesis_zmvm.duckdb", "QA Validator: src/data_quality/validator.py")
    G.add_edge("Script: scripts/inicializar_base_datos.py", "Schema: src/database/schema.py")
    G.add_edge("Script: scripts/inicializar_base_datos.py", "QA Validator: src/data_quality/validator.py")
    G.add_edge("generar_pdf_propuesta.py", "Doc: Propuesta_Tesis_Carlos_Mayorga_Anahuac.pdf")
    
    # Generar Representación Mermaid para Markdown
    mermaid_lines = ["```mermaid", "graph TD"]
    for src, dst in G.edges():
        s_clean = src.replace(":", "_").replace("/", "_").replace(".", "_").replace(" ", "_").replace("(", "").replace(")", "")
        d_clean = dst.replace(":", "_").replace("/", "_").replace(".", "_").replace(" ", "_").replace("(", "").replace(")", "")
        mermaid_lines.append(f'    {s_clean}["{src}"] --> {d_clean}["{dst}"]')
    mermaid_lines.append("```")
    mermaid_str = "\n".join(mermaid_lines)
    
    md_content = f"""# 🕸️ Grafo de Arquitectura del Proyecto (Graphify)
## Maestría en Estadística — Universidad Anáhuac México Norte

Este documento mapea las relaciones de dependencia entre fuentes de datos, módulos de código, base de datos analítica y salidas del proyecto.

### Diagrama de Grafo de Flujo

{mermaid_str}

### Resumen de Nodos de la Arquitectura
* **Fuentes de Datos (Sources):** SHF, ENOE, DENUE, Inside Airbnb CDMX.
* **Capa de Almacenamiento:** DuckDB (`processed_data/tesis_zmvm.duckdb`).
* **Módulos de Código:** `src/database/schema.py`, `src/data_quality/validator.py`.
* **Entregables Principales:** `Propuesta_Tesis_Carlos_Mayorga_Anahuac.pdf`, `heartbeat.md`.
"""
    
    out_md = "docs/architecture_graph.md"
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    print(f"[✔] Grafo de arquitectura generado exitosamente en: {out_md}")
    print("="*70)

if __name__ == "__main__":
    generate_graph()
