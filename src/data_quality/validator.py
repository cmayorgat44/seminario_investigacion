import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller, kpss

class TimeSeriesDataValidator:
    """
    Suite de validación de calidad y pruebas de robustez estadística para series de tiempo
    socioeconómicas y demográficas.
    """
    def __init__(self, df: pd.DataFrame, time_col: str = 'id_trimestre'):
        self.df = df
        self.time_col = time_col

    def check_temporal_continuity(self, start_year=2005, end_year=2024):
        """
        Verifica la continuidad temporal estricta de los 80 trimestres esperados.
        """
        expected_quarters = [f"{y}Q{q}" for y in range(start_year, end_year + 1) for q in range(1, 5)]
        present_quarters = self.df[self.time_col].unique()
        missing = set(expected_quarters) - set(present_quarters)
        
        status = len(missing) == 0
        return {
            "is_continuous": status,
            "total_expected": len(expected_quarters),
            "total_present": len(present_quarters),
            "missing_quarters": sorted(list(missing))
        }

    def detect_outliers_mad(self, series: pd.Series, threshold: float = 3.5):
        """
        Detección robusta de valores atípicos basada en la Desviación Absoluta de la Mediana (MAD).
        """
        median = series.median()
        mad = (series - median).abs().median()
        if mad == 0:
            modified_z_score = np.zeros(len(series))
        else:
            modified_z_score = 0.6745 * (series - median).abs() / mad
            
        outliers_mask = modified_z_score > threshold
        return {
            "outliers_count": outliers_mask.sum(),
            "outliers_pct": (outliers_mask.sum() / len(series)) * 100,
            "outlier_indices": series[outliers_mask].index.tolist()
        }

    def evaluate_stationarity(self, series: pd.Series, max_lags: int = 4):
        """
        Ejecuta pruebas de Raíz Unitaria (ADF) y Estacionariedad (KPSS)
        para determinar formalmente el orden de integración I(d).
        """
        s_clean = series.dropna()
        if len(s_clean) < 15:
            return {"error": "Insuficientes datos para prueba de integrabilidad"}
            
        # ADF Test (H0: La serie tiene raíz unitaria / NO es estacionaria)
        adf_res = adfuller(s_clean, maxlag=max_lags, autolag='AIC')
        adf_pvalue = adf_res[1]
        
        # KPSS Test (H0: La serie ES estacionaria)
        try:
            kpss_res = kpss(s_clean, regression='c', nlags='auto')
            kpss_pvalue = kpss_res[1]
        except Exception:
            kpss_pvalue = np.nan
            
        # Clasificación estocástica
        if adf_pvalue < 0.05 and (np.isnan(kpss_pvalue) or kpss_pvalue >= 0.05):
            integration_order = "I(0) Estacionaria"
        elif adf_pvalue >= 0.05 and kpss_pvalue < 0.05:
            integration_order = "I(1) Raíz Unitaria (Requiere diferenciación)"
        else:
            integration_order = "Indeterminada / Tendencia no estacionaria"

        return {
            "adf_stat": adf_res[0],
            "adf_pvalue": adf_pvalue,
            "kpss_stat": kpss_res[0] if not np.isnan(kpss_pvalue) else None,
            "kpss_pvalue": kpss_pvalue,
            "orden_integracion_estimado": integration_order
        }

def run_pipeline_qa(df: pd.DataFrame, target_columns: list):
    """
    Ejecuta el diagnóstico integral de calidad sobre el dataframe analítico.
    """
    validator = TimeSeriesDataValidator(df)
    print("="*70)
    print("  DIAGNÓSTICO DE ROBUSTEZ Y PRUEBAS DE CALIDAD ESTADÍSTICA (QA)")
    print("="*70)
    
    # 1. Continuidad
    cont_res = validator.check_temporal_continuity()
    print(f"[*] Continuidad Temporal (2005Q1 - 2024Q4):")
    print(f"    • Esperados: {cont_res['total_expected']} | Presentes: {cont_res['total_present']}")
    print(f"    • ¿Continuo?: {'[✔] SÍ' if cont_res['is_continuous'] else '[✘] FALTAN PERIODOS'}")
    if not cont_res['is_continuous']:
        print(f"    • Faltantes: {cont_res['missing_quarters']}")
        
    print("\n" + "-"*70)
    print(" 2. DETECCIÓN DE VALORES ATÍPICOS Y PRUEBAS DE INTEGRABILIDAD I(d)")
    print("-"*70)
    
    qa_summary = []
    for col in target_columns:
        if col in df.columns:
            s = df[col]
            outlier_info = validator.detect_outliers_mad(s)
            stat_info = validator.evaluate_stationarity(s)
            
            qa_summary.append({
                "Variable": col,
                "Nulos": s.isna().sum(),
                "Atípicos (MAD)": f"{outlier_info['outliers_count']} ({outlier_info['outliers_pct']:.1f}%)",
                "ADF p-value": f"{stat_info['adf_pvalue']:.4f}" if 'adf_pvalue' in stat_info else "N/A",
                "KPSS p-value": f"{stat_info['kpss_pvalue']:.4f}" if 'kpss_pvalue' in stat_info and stat_info['kpss_pvalue'] else "N/A",
                "Orden I(d)": stat_info.get("orden_integracion_estimado", "N/A")
            })
            
    df_qa = pd.DataFrame(qa_summary)
    print(df_qa.to_string(index=False))
    print("="*70)
    return df_qa
