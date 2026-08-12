import os
import subprocess
import pandas as pd
import numpy as np

def download_fred_md(output_path="raw_data/fred_md_current.csv"):
    """
    Descarga el archivo current.csv de FRED-MD si no existe localmente usando curl.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if os.path.exists(output_path):
        print(f"[✔] Archivo FRED-MD ya existe localmente en: {output_path}")
        return output_path

    url = "https://www.stlouisfed.org/-/media/project/frbstl/stlouisfed/research/fred-md/monthly/2026-07-md.csv"
    print(f"Descargando datos de FRED-MD desde: {url} usando curl...")
    
    try:
        subprocess.run([
            "curl", "-L", "-o", output_path, url
        ], check=True)
        print(f"[✔] Descargado exitosamente en: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error al descargar con curl: {e}")
        raise e
        
    return output_path

def apply_transformation(series, code):
    """
    Aplica las transformaciones de estacionariedad estándar de FRED-MD:
    1. Sin transformación: x_t = y_t
    2. Primera diferencia: x_t = y_t - y_{t-1}
    3. Segunda diferencia: x_t = (y_t - y_{t-1}) - (y_{t-1} - y_{t-2})
    4. Logaritmo natural: x_t = ln(y_t)
    5. Primera diferencia de logaritmos: x_t = ln(y_t) - ln(y_{t-1})
    6. Segunda diferencia de logaritmos: x_t = (ln(y_t) - ln(y_{t-1})) - (ln(y_{t-1}) - ln(y_{t-2}))
    7. Primera diferencia del cambio porcentual: x_t = (y_t / y_{t-1} - 1) - (y_{t-1} / y_{t-2} - 1)
    """
    # Evitar warnings de copia y asegurar tipos
    s = series.astype(float)
    
    if code == 1:
        return s
    elif code == 2:
        return s.diff()
    elif code == 3:
        return s.diff().diff()
    elif code == 4:
        return np.log(s)
    elif code == 5:
        return np.log(s).diff()
    elif code == 6:
        return np.log(s).diff().diff()
    elif code == 7:
        return (s.pct_change()).diff()
    else:
        return s

def load_and_clean_fred_md(file_path="raw_data/fred_md_current.csv", start_date="1959-01-01", end_date="2001-08-01"):
    """
    Carga, transforma y estandariza los datos de FRED-MD.
    Retorna:
        - df_transformed: DataFrame estandarizado de factores macroeconómicos (X)
        - y_series: La tasa de política monetaria (FEDFUNDS) sin estandarizar
        - t_codes: Diccionario con los códigos de transformación aplicados
    """
    # Leer el archivo crudo. La primera fila (índice 0) tiene los nombres de variables.
    # La segunda fila (índice 1) contiene los códigos de transformación (transform).
    raw_df = pd.read_csv(file_path)
    
    # Extraer los códigos de transformación (segunda fila)
    # La primera columna es la fecha ("sasdate"), que no tiene código de transformación
    t_codes_series = raw_df.iloc[0]
    t_codes = {col: int(t_codes_series[col]) for col in raw_df.columns if col != 'sasdate' and pd.notna(t_codes_series[col])}
    
    # El resto del DataFrame contiene los datos. Nos saltamos la fila de códigos de transformación.
    data_df = raw_df.iloc[1:].copy()
    
    # Limpiar y parsear la columna de fecha
    data_df['sasdate'] = pd.to_datetime(data_df['sasdate'], format='%m/%d/%Y', errors='coerce')
    data_df = data_df.dropna(subset=['sasdate'])
    data_df = data_df.set_index('sasdate')
    
    # Eliminar filas completamente vacías al final del archivo (suelen existir notas de pie)
    data_df = data_df.dropna(how='all')
    
    # Filtrar por rango de fechas para replicar el período de BBE (1959-01 a 2001-08)
    data_df = data_df.loc[start_date:end_date]
    
    # Procesar transformaciones de estacionariedad columna por columna
    transformed_cols = {}
    for col in t_codes:
        if col in data_df.columns:
            transformed_cols[col] = apply_transformation(data_df[col], t_codes[col])
            
    transformed_df = pd.DataFrame(transformed_cols, index=data_df.index)
    
    # Remover el primer y segundo renglón del dataset transformado debido a pérdidas por diferencias de primer y segundo orden
    transformed_df = transformed_df.iloc[2:]
    
    # Extraer la variable de interés (política monetaria: FEDFUNDS)
    # Bernanke et al. (2005) usan FEDFUNDS como la variable de política monetaria (Y) observada directamente.
    if 'FEDFUNDS' not in transformed_df.columns:
        raise ValueError("FEDFUNDS (Federal Funds Rate) no encontrada en el dataset. Es indispensable para la replicación del choque monetario.")
        
    y_series = transformed_df['FEDFUNDS'].copy()
    
    # Limpiar variables con datos faltantes. Para PCA no se admiten NaNs.
    # Eliminamos columnas que tengan más del 5% de NaNs en el periodo seleccionado
    missing_pct = transformed_df.isna().mean()
    cols_to_keep = missing_pct[missing_pct <= 0.05].index
    
    clean_df = transformed_df[cols_to_keep].copy()
    
    # Imputar el resto de los faltantes mínimos con interpolación lineal y retro-llenado
    clean_df = clean_df.interpolate(method='linear').bfill().ffill()
    
    # Separar la matriz X (excluyendo la tasa de política monetaria para estimar los factores puros de X)
    x_df = clean_df.drop(columns=['FEDFUNDS'])
    
    # Estandarizar X (media 0, desviación estándar 1) como requiere la teoría de factores por componentes principales
    x_standardized = (x_df - x_df.mean()) / x_df.std()
    
    print(f"[✔] Dataset limpio y transformado para el periodo {start_date} a {end_date}.")
    print(f"    - Series en X (Macro): {x_standardized.shape[1]} columnas, {x_standardized.shape[0]} observaciones.")
    print(f"    - Serie en Y (FEDFUNDS): {y_series.shape[0]} observaciones.")
    
    return x_standardized, y_series, t_codes

if __name__ == "__main__":
    raw_path = download_fred_md()
    X, Y, codes = load_and_clean_fred_md(raw_path)
