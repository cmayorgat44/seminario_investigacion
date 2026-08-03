import os
import duckdb

def init_duckdb_schema(db_path="processed_data/tesis_zmvm.duckdb"):
    """
    Inicializa la estructura relacional normalizada (Esquema Estrella / 3NF)
    en DuckDB para garantizar integridad referencial y alto rendimiento.
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = duckdb.connect(db_path)
    
    # 1. Tabla Dimensional: Alcaldías y Municipios ZMVM
    conn.execute("""
    CREATE TABLE IF NOT EXISTS dim_alcaldia (
        id_alcaldia VARCHAR PRIMARY KEY,
        nombre_alcaldia VARCHAR NOT NULL,
        entidad VARCHAR NOT NULL,
        cve_geo VARCHAR UNIQUE,
        es_central BOOLEAN DEFAULT FALSE
    );
    """)
    
    # 2. Tabla Dimensional: Tiempo Trimestral (2005Q1 - 2024Q4 = 80 periodos)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS dim_tiempo (
        id_trimestre VARCHAR PRIMARY KEY, -- Ej: '2024Q1'
        anio INTEGER NOT NULL,
        trimestre INTEGER NOT NULL,
        fecha_inicio DATE NOT NULL,
        fecha_fin DATE NOT NULL
    );
    """)
    
    # 3. Tabla de Hechos: Índice SHF de Vivienda
    conn.execute("""
    CREATE TABLE IF NOT EXISTS fact_shf_precios (
        id_trimestre VARCHAR REFERENCES dim_tiempo(id_trimestre),
        id_alcaldia VARCHAR REFERENCES dim_alcaldia(id_alcaldia),
        indice_shf DOUBLE,
        variacion_anual_pct DOUBLE,
        precio_mediano_m2 DOUBLE,
        PRIMARY KEY (id_trimestre, id_alcaldia)
    );
    """)
    
    # 4. Tabla de Hechos: Métricas de Alojamiento Temporal (Airbnb)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS fact_airbnb_metricas (
        id_trimestre VARCHAR REFERENCES dim_tiempo(id_trimestre),
        id_alcaldia VARCHAR REFERENCES dim_alcaldia(id_alcaldia),
        total_listings INTEGER,
        listings_vivienda_completa INTEGER,
        pct_vivienda_completa DOUBLE,
        precio_mediano_noche DOUBLE,
        revpar_estimado DOUBLE,
        PRIMARY KEY (id_trimestre, id_alcaldia)
    );
    """)
    
    # 5. Tabla de Hechos: Empleo y Movilidad Laboral (ENOE)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS fact_enoe_movilidad (
        id_trimestre VARCHAR REFERENCES dim_tiempo(id_trimestre),
        id_alcaldia VARCHAR REFERENCES dim_alcaldia(id_alcaldia),
        saldo_migratorio_neto DOUBLE,
        ingreso_medio_hora DOUBLE,
        tasa_informalidad DOUBLE,
        desocupacion_pct DOUBLE,
        PRIMARY KEY (id_trimestre, id_alcaldia)
    );
    """)
    
    # 6. Tabla de Hechos: Gentrificación Comercial (DENUE)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS fact_denue_comercio (
        id_trimestre VARCHAR REFERENCES dim_tiempo(id_trimestre),
        id_alcaldia VARCHAR REFERENCES dim_alcaldia(id_alcaldia),
        unidades_gentrificadoras INTEGER,
        densidad_km2 DOUBLE,
        tasa_apertura_anual DOUBLE,
        PRIMARY KEY (id_trimestre, id_alcaldia)
    );
    """)
    
    # Vista Analítica Unificada (Panel Multivariado para FAVAR-VECM)
    conn.execute("""
    CREATE VIEW IF NOT EXISTS vista_panel_multivariado AS
    SELECT 
        t.id_trimestre,
        t.anio,
        t.trimestre,
        a.id_alcaldia,
        a.nombre_alcaldia,
        a.es_central,
        s.indice_shf,
        b.total_listings AS airbnb_listings,
        b.pct_vivienda_completa AS airbnb_pct_completa,
        b.precio_mediano_noche AS airbnb_precio_mediano,
        e.saldo_migratorio_neto AS enoe_saldo_migratorio,
        e.ingreso_medio_hora AS enoe_ingreso_hora,
        d.unidades_gentrificadoras AS denue_unidades_comerciales
    FROM dim_tiempo t
    CROSS JOIN dim_alcaldia a
    LEFT JOIN fact_shf_precios s ON t.id_trimestre = s.id_trimestre AND a.id_alcaldia = s.id_alcaldia
    LEFT JOIN fact_airbnb_metricas b ON t.id_trimestre = b.id_trimestre AND a.id_alcaldia = b.id_alcaldia
    LEFT JOIN fact_enoe_movilidad e ON t.id_trimestre = e.id_trimestre AND a.id_alcaldia = e.id_alcaldia
    LEFT JOIN fact_denue_comercio d ON t.id_trimestre = d.id_trimestre AND a.id_alcaldia = d.id_alcaldia;
    """)
    
    conn.close()
    print(f"[✔] Esquema relacional relacional DuckDB inicializado correctamente en: {db_path}")

if __name__ == "__main__":
    init_duckdb_schema()
