import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Agregar src/ al path para poder importar favar
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.favar.data_loader import download_fred_md, load_and_clean_fred_md
from src.favar.model import FAVAR

def main():
    # 1. Descargar y procesar datos de FRED-MD
    raw_path = download_fred_md()
    X, Y, codes = load_and_clean_fred_md(raw_path)
    
    # 2. Identificar variables financieras rápidas (Fast-moving variables)
    # Típicamente tasas de interés, tipos de cambio y precios de acciones
    fast_patterns = ['TB3', 'TB6', 'GS1', 'GS5', 'GS10', 'AAA', 'BAA', 'EXSZ', 'EXJP', 'EXUS', 'EXCA', 'SP500', 'S&P', 'COMPAP', 'CP3M', 'WUIDEST']
    fast_moving_cols = [col for col in X.columns if any(p in col for p in fast_patterns)]
    
    print(f"Detectadas {len(fast_moving_cols)} variables financieras rápidas de {X.shape[1]} totales.")
    
    # 3. Ajustar el modelo FAVAR
    # Especificación de BBE (2005): K=3 factores, p=13 rezagos
    k = 3
    p = 13
    periods = 48
    model = FAVAR(n_factors=k, lags=p)
    model.fit(X, Y, fast_moving_cols)
    
    # 4. Calcular el choque de Política Monetaria
    # Shock de +25 puntos base (0.25) en FEDFUNDS
    irf_df = model.compute_irf(periods=periods, impulse_size=0.25)
    
    # 5. Proyectar y transformar las respuestas a niveles para variables clave
    key_vars = {
        'INDPRO': 'Producción Industrial',
        'CPIAUCSL': 'Índice de Precios al Consumidor (IPC)',
        'PAYEMS': 'Empleo Total No Agrícola',
        'HOUST': 'Inicios de Construcción de Vivienda',
        'GS10': 'Rendimiento Bono del Tesoro a 10 Años'
    }
    
    projected_irfs = {}
    for var, label in key_vars.items():
        if var in X.columns:
            # Obtener respuesta cruda (diferenciada/estandarizada)
            raw_irf = model.get_macro_variable_irf(var, irf_df)
            
            # Recuperar el código de transformación
            code = codes.get(var, 1)
            
            # Re-escalar y aplicar sumas acumulativas según la transformación para volver a niveles
            # Si fue diferenciado una vez (2, 5) -> suma acumulativa simple
            # Si fue diferenciado dos veces (3, 6) -> suma acumulativa doble
            if code in [2, 5]:
                level_irf = np.cumsum(raw_irf)
            elif code in [3, 6]:
                level_irf = np.cumsum(np.cumsum(raw_irf))
            else:
                level_irf = raw_irf
                
            projected_irfs[var] = level_irf
        else:
            print(f"[!] Advertencia: Variable {var} no disponible en X.")
            
    # Agregar la respuesta de la propia tasa de interés (FEDFUNDS)
    # Como FEDFUNDS no está en X sino que es Y directamente, su respuesta ya está en niveles (código 1)
    projected_irfs['FEDFUNDS'] = irf_df['FEDFUNDS'].values
    
    # 6. Graficar las Funciones de Impulso-Respuesta
    print("Graficando funciones de impulso-respuesta...")
    fig, axes = plt.subplots(3, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    # Lista de variables a graficar
    plot_vars = [
        ('FEDFUNDS', 'Tasa de Interés Federal (FEDFUNDS)', '%'),
        ('INDPRO', 'Producción Industrial (INDPRO)', 'Log-Nivel'),
        ('CPIAUCSL', 'Índice de Precios al Consumidor (IPC)', 'Log-Nivel'),
        ('PAYEMS', 'Empleo Total (PAYEMS)', 'Log-Nivel'),
        ('HOUST', 'Inicios de Vivienda (HOUST)', 'Log-Nivel'),
        ('GS10', 'Bono del Tesoro a 10 Años (GS10)', '%')
    ]
    
    for i, (var, label, unit) in enumerate(plot_vars):
        ax = axes[i]
        if var in projected_irfs:
            irf_val = projected_irfs[var]
            ax.plot(irf_val, color='#1f77b4', linewidth=2.5, label='Respuesta FAVAR')
            ax.axhline(0, color='red', linestyle='--', linewidth=1)
            ax.set_title(f"{label}", fontsize=12, fontweight='bold')
            ax.set_xlabel("Meses post-choque", fontsize=9)
            ax.set_ylabel(unit, fontsize=9)
            ax.grid(True, linestyle=':', alpha=0.6)
        else:
            ax.text(0.5, 0.5, "Variable no disponible", ha='center', va='center')
            
    plt.suptitle("Funciones de Impulso-Respuesta (IRF) ante un Choque Contractivo de Política Monetaria (+25 pb)\nModelo FAVAR (K=3, p=13) - Réplica de Bernanke, Boivin y Eliasz (2005)", fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout()
    
    # Guardar gráficos en processed_data y en el directorio de artefactos
    os.makedirs("processed_data", exist_ok=True)
    plot_path_local = "processed_data/bbe_2005_replication.png"
    plt.savefig(plot_path_local, dpi=300, bbox_inches='tight')
    print(f"[✔] Gráfico guardado localmente en: {plot_path_local}")
    
    # Ruta de artefacto del agente
    artifact_dir = "/Users/carlosmayorga/.gemini/antigravity-ide/brain/8b0e7b7d-f72a-45fe-98dd-0fc9aa3f0e27"
    if os.path.exists(artifact_dir):
        plot_path_artifact = os.path.join(artifact_dir, "bbe_2005_replication.png")
        plt.savefig(plot_path_artifact, dpi=300, bbox_inches='tight')
        print(f"[✔] Gráfico guardado en artefactos: {plot_path_artifact}")
        
    plt.close()

if __name__ == "__main__":
    main()
