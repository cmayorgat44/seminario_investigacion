import os
import requests
import pandas as pd

def check_endpoint(url, name):
    print(f"[*] Comprobando {name}...")
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
    try:
        r = requests.get(url, headers=headers, timeout=4, allow_redirects=True)
        size = len(r.content)
        size_kb = size / 1024
        print(f"    [✔] Respuesta OK: Código HTTP {r.status_code} ({size_kb:.1f} KB recibidos)")
        return True, r.status_code, f"{size_kb:.1f} KB"
    except Exception as e:
        print(f"    [✘] No se pudo verificar vía solicitud directa: {e}")
        return False, "Error/Timeout", "N/A"

def main():
    print("="*70)
    print("  DIAGNÓSTICO TÉCNICO DE FUENTES DE DATOS ABIERTOS")
    print("="*70)
    
    os.makedirs("raw_data", exist_ok=True)
    os.makedirs("processed_data", exist_ok=True)
    
    # Endpoints de prueba
    sources = [
        ("Inside Airbnb CDMX (Summary)", "https://data.insideairbnb.com/mexico/df/mexico-city/2024-03-29/visualisations/listings.csv"),
        ("Portal Descarga Masiva INEGI", "https://www.inegi.org.mx/app/descarga/?ti=6"),
        ("Portal SHF (Índice de Precios)", "https://www.gob.mx/shf"),
        ("Portal INEGI (ENOE)", "https://www.inegi.org.mx/programas/enoe/15ymas/")
    ]
    
    results = []
    for name, url in sources:
        ok, code, size = check_endpoint(url, name)
        results.append({
            "Fuente": name,
            "Conexión": "Exitosa" if ok else "Requiere descarga manual / portal",
            "Código HTTP": code,
            "Respuesta": size
        })
        
    print("\n" + "="*70)
    print("  MATRIZ DE EVALUACIÓN DE DATOS ABIERTOS PARA EL MODELO FAVAR-VECM")
    print("="*70)
    
    eval_matrix = [
        {
            "Dataset": "1. Índice SHF Vivienda",
            "Frecuencia": "Trimestral",
            "Cobertura": "ZMVM / Alcaldías",
            "Periodo": "2005 - 2024",
            "Viabilidad": "ALTA (Formatos Excel/CSV oficiales)",
            "Acción Requerida": "Descargar serie histórica de gob.mx/shf"
        },
        {
            "Dataset": "2. INEGI ENOE",
            "Frecuencia": "Trimestral",
            "Cobertura": "ZMVM / Nacional",
            "Periodo": "2005 - 2024",
            "Viabilidad": "ALTA (Microdatos públicos CSV)",
            "Acción Requerida": "Procesar variables de migración e ingresos"
        },
        {
            "Dataset": "3. INEGI DENUE",
            "Frecuencia": "Semestral",
            "Cobertura": "AGEB / Municipio",
            "Periodo": "2010 - 2024",
            "Viabilidad": "ALTA (Descarga masiva INEGI)",
            "Acción Requerida": "Filtrar giros gentrificadores (SCIAN)"
        },
        {
            "Dataset": "4. Inside Airbnb CDMX",
            "Frecuencia": "Mensual/Trim",
            "Cobertura": "Alcaldías CDMX",
            "Periodo": "2015 - 2024",
            "Viabilidad": "ALTA (Listings CSV públicos)",
            "Acción Requerida": "Agregar densidad de alquiler por alcaldía"
        }
    ]
    
    df_eval = pd.DataFrame(eval_matrix)
    print(df_eval.to_string(index=False))
    print("="*70)

if __name__ == "__main__":
    main()
