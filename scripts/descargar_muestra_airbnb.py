import os
import urllib.request
import pandas as pd

def main():
    print("="*70)
    print("  DESCARGA E INSPECCIÓN DE MUESTRA REAL: INSIDE AIRBNB CDMX")
    print("="*70)
    
    raw_dir = "raw_data"
    os.makedirs(raw_dir, exist_ok=True)
    csv_path = os.path.join(raw_dir, "airbnb_cdmx_summary.csv")
    
    url = "https://data.insideairbnb.com/mexico/df/mexico-city/2024-03-29/visualisations/listings.csv"
    
    print(f"[*] Descargando dataset desde {url}...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response, open(csv_path, 'wb') as out_file:
            out_file.write(response.read())
        print(f"[✔] Archivo descargado exitosamente en: {csv_path}")
        
        # Leer y analizar estructura
        df = pd.read_csv(csv_path)
        print("\n--- Vista Previa de la Estructura de Datos (Primeros 5 registros) ---")
        print(df[['id', 'name', 'neighbourhood', 'latitude', 'longitude', 'room_type', 'price', 'number_of_reviews']].head())
        
        print("\n--- Distribución de Alojamientos por Alcaldía (Top 10) ---")
        print(df['neighbourhood'].value_counts().head(10))
        
        print("\n--- Distribución por Tipo de Habitación ---")
        print(df['room_type'].value_counts(normalize=True) * 100)
        
        print("\n[✔] Inspección completada. El dataset de Airbnb es 100% utilizable.")
        
    except Exception as e:
        print(f"[✘] Ocurrió un error al descargar/analizar: {e}")

if __name__ == "__main__":
    main()
