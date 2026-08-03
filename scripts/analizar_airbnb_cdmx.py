import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    print("="*70)
    print("  ANÁLISIS EXPLORATORIO DE DATOS: INSIDE AIRBNB CDMX")
    print("="*70)
    
    file_path = "raw_data/airbnb_cdmx_summary.csv"
    if not os.path.exists(file_path):
        print(f"[✘] No se encontró el archivo: {file_path}")
        return
        
    df = pd.read_csv(file_path)
    print(f"[✔] Registros totales cargados: {len(df):,}")
    print(f"[✔] Columnas disponibles ({len(df.columns)}): {list(df.columns)}")
    
    print("\n" + "-"*70)
    print(" 1. DISTRIBUCIÓN DE ALOJAMIENTOS POR ALCALDÍA (TOP 10)")
    print("-"*70)
    alcaldia_counts = df['neighbourhood'].value_counts()
    for alc, count in alcaldia_counts.head(10).items():
        pct = (count / len(df)) * 100
        print(f"  • {alc:<25}: {count:5,} propiedades ({pct:5.2f}%)")
        
    print("\n" + "-"*70)
    print(" 2. PRECIO PROMEDIO Y MEDIANA POR NOCHE (MXN) POR ALCALDÍA (TOP 10)")
    print("-"*70)
    # Filtrar precios atípicos para la mediana y promedio
    df_clean_price = df[df['price'] > 0].copy()
    price_stats = df_clean_price.groupby('neighbourhood')['price'].agg(['count', 'mean', 'median']).loc[alcaldia_counts.head(10).index]
    price_stats.columns = ['Total Propiedades', 'Precio Promedio ($)', 'Precio Mediana ($)']
    print(price_stats.to_string())
    
    print("\n" + "-"*70)
    print(" 3. TIPOLOGÍA DE ALOJAMIENTOS")
    print("-"*70)
    room_stats = df['room_type'].value_counts()
    for rtype, count in room_stats.items():
        pct = (count / len(df)) * 100
        print(f"  • {rtype:<25}: {count:5,} ({pct:5.2f}%)")
        
    # Guardar resumen procesado en processed_data
    out_summary = "processed_data/resumen_airbnb_por_alcaldia.csv"
    price_stats.to_csv(out_summary)
    print(f"\n[✔] Resumen guardado exitosamente en: {out_summary}")
    print("="*70)

if __name__ == "__main__":
    main()
