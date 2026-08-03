import os
import sys
import duckdb
import pandas as pd
import numpy as np

# Agregar directorio raíz al PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database.schema import init_duckdb_schema
from src.data_quality.validator import run_pipeline_qa

def populate_dimensions(conn):
    print("[*] Poblando tablas dimensionales (dim_alcaldia, dim_tiempo)...")
    
    # 1. Poblar Dimensión Alcaldías ZMVM (5 columnas: id, nombre, entidad, cve_geo, es_central)
    alcaldias_data = [
        ('09003', 'Coyoacán', 'Ciudad de México', '09003', True),
        ('09004', 'Cuajimalpa de Morelos', 'Ciudad de México', '09004', False),
        ('09005', 'Gustavo A. Madero', 'Ciudad de México', '09005', False),
        ('09006', 'Iztacalco', 'Ciudad de México', '09006', False),
        ('09007', 'Iztapalapa', 'Ciudad de México', '09007', False),
        ('09008', 'La Magdalena Contreras', 'Ciudad de México', '09008', False),
        ('09009', 'Milpa Alta', 'Ciudad de México', '09009', False),
        ('09010', 'Álvaro Obregón', 'Ciudad de México', '09010', False),
        ('09011', 'Tláhuac', 'Ciudad de México', '09011', False),
        ('09012', 'Tlalpan', 'Ciudad de México', '09012', False),
        ('09013', 'Xochimilco', 'Ciudad de México', '09013', False),
        ('09014', 'Benito Juárez', 'Ciudad de México', '09014', True),
        ('09015', 'Cuauhtémoc', 'Ciudad de México', '09015', True),
        ('09016', 'Miguel Hidalgo', 'Ciudad de México', '09016', True),
        ('09017', 'Venustiano Carranza', 'Ciudad de México', '09017', False),
        ('15033', 'Ecatepec de Morelos', 'Estado de México', '15033', False),
        ('15057', 'Nezahualcóyotl', 'Estado de México', '15057', False),
        ('15058', 'Naucalpan de Juárez', 'Estado de México', '15058', False),
        ('15104', 'Tlalnepantla de Baz', 'Estado de México', '15104', False),
    ]
    df_alc = pd.DataFrame(alcaldias_data, columns=['id_alcaldia', 'nombre_alcaldia', 'entidad', 'cve_geo', 'es_central'])
    conn.execute("DELETE FROM dim_alcaldia")
    conn.execute("INSERT INTO dim_alcaldia SELECT * FROM df_alc")
    
    # 2. Poblar Dimensión Tiempo Trimestral (2005Q1 - 2024Q4 = 80 trimestres)
    tiempo_rows = []
    for year in range(2005, 2025):
        for q in range(1, 5):
            id_q = f"{year}Q{q}"
            m_start = (q - 1) * 3 + 1
            fecha_start = f"{year}-{m_start:02d}-01"
            m_end = q * 3
            fecha_end = f"{year}-{m_end:02d}-28"
            tiempo_rows.append((id_q, year, q, fecha_start, fecha_end))
            
    df_tiempo = pd.DataFrame(tiempo_rows, columns=['id_trimestre', 'anio', 'trimestre', 'fecha_inicio', 'fecha_fin'])
    conn.execute("DELETE FROM dim_tiempo")
    conn.execute("INSERT INTO dim_tiempo SELECT * FROM df_tiempo")
    print(f"    [✔] Dimensiones cargadas: {len(df_alc)} alcaldías | {len(df_tiempo)} trimestres.")

def populate_fact_airbnb(conn):
    airbnb_path = "raw_data/airbnb_cdmx_summary.csv"
    if os.path.exists(airbnb_path):
        print(f"[*] Procesando e insertando hechos de Airbnb desde: {airbnb_path}...")
        df_raw = pd.read_csv(airbnb_path)
        
        # Mapear nombres de alcaldías a IDs
        df_alc = conn.execute("SELECT id_alcaldia, nombre_alcaldia FROM dim_alcaldia").df()
        alcaldia_map = dict(zip(df_alc['nombre_alcaldia'], df_alc['id_alcaldia']))
        
        # Agrupar métricas por alcaldía
        df_clean = df_raw[df_raw['price'] > 0].copy()
        df_clean['is_entire'] = df_clean['room_type'] == 'Entire home/apt'
        
        grp = df_clean.groupby('neighbourhood').agg(
            total_listings=('id', 'count'),
            listings_vivienda_completa=('is_entire', 'sum'),
            precio_mediano_noche=('price', 'median')
        ).reset_index()
        
        grp['id_alcaldia'] = grp['neighbourhood'].map(alcaldia_map)
        grp['pct_vivienda_completa'] = (grp['listings_vivienda_completa'] / grp['total_listings']) * 100
        grp['revpar_estimado'] = grp['precio_mediano_noche'] * 0.60 # Estimador proxy
        
        # Insertar para el trimestre más reciente (2024Q2)
        grp['id_trimestre'] = '2024Q2'
        
        df_fact = grp[['id_trimestre', 'id_alcaldia', 'total_listings', 'listings_vivienda_completa', 
                       'pct_vivienda_completa', 'precio_mediano_noche', 'revpar_estimado']].dropna()
        
        conn.execute("DELETE FROM fact_airbnb_metricas WHERE id_trimestre = '2024Q2'")
        conn.execute("INSERT INTO fact_airbnb_metricas SELECT * FROM df_fact")
        print(f"    [✔] Hechos de Airbnb insertados exitosamente ({len(df_fact)} registros).")

def main():
    db_path = "processed_data/tesis_zmvm.duckdb"
    init_duckdb_schema(db_path)
    
    conn = duckdb.connect(db_path)
    populate_dimensions(conn)
    populate_fact_airbnb(conn)
    
    # Extraer panel unificado de la vista analítica para QA
    df_panel = conn.execute("SELECT * FROM vista_panel_multivariado").df()
    conn.close()
    
    print("\n[*] Ejecutando suite de pruebas de robustez estadística (QA)...")
    run_pipeline_qa(df_panel, target_columns=['airbnb_listings', 'airbnb_precio_mediano', 'airbnb_pct_completa'])

if __name__ == "__main__":
    main()
