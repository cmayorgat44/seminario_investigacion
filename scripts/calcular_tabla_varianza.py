import os
import sys
import json
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.favar.data_loader import download_fred_md, load_and_clean_fred_md
from src.favar.model import FAVAR

def main():
    raw_path = download_fred_md()
    X, Y, codes = load_and_clean_fred_md(raw_path)
    
    fast_patterns = ['TB3', 'TB6', 'GS1', 'GS5', 'GS10', 'AAA', 'BAA', 'EXSZ', 'EXJP', 'EXUS', 'EXCA', 'SP500', 'S&P', 'COMPAP', 'CP3M']
    fast_moving_cols = [col for col in X.columns if any(p in col for p in fast_patterns)]
    
    model = FAVAR(n_factors=3, lags=13)
    model.fit(X, Y, fast_moving_cols)
    
    var_result = model.var_result
    sigma_u = var_result.sigma_u
    H = np.linalg.cholesky(sigma_u)
    
    n_vars = 3 + 1
    lags = 13
    periods = 60
    
    params = var_result.params
    if 'const' in params.index:
        params_no_const = params.drop('const')
    else:
        params_no_const = params
    
    coefs = np.zeros((lags, n_vars, n_vars))
    for l in range(lags):
        coefs[l] = params_no_const.iloc[l*n_vars:(l+1)*n_vars].values.T
        
    Psi = np.zeros((periods, n_vars, n_vars))
    Psi[0] = H
    
    for j in range(1, periods):
        temp = np.zeros((n_vars, n_vars))
        for l in range(min(j, lags)):
            temp += np.dot(coefs[l], Psi[j - 1 - l])
        Psi[j] = temp
        
    Lambda_F = model.loading_f.values
    Lambda_Y = model.loading_y.values.reshape(-1, 1)
    Lambda = np.hstack([Lambda_F, Lambda_Y])
    
    table_mapping = {
        'Federal funds rate': ('FEDFUNDS', True, 0.4538, 1.0000),
        'Industrial production': ('INDPRO', False, 0.0763, 0.7074),
        'Consumer price index': ('CPIAUCSL', False, 0.0441, 0.8699),
        '3-month treasury bill': ('TB3MS', False, 0.4440, 0.9751),
        '5-year bond': ('GS5', False, 0.4354, 0.9250),
        'Monetary Base': ('BOGMBASE', False, 0.0500, 0.1039),
        'M2': ('M2SL', False, 0.1035, 0.0518),
        'Exchange rate (Yen/$)': ('EXJPUSx', False, 0.2816, 0.0252),
        'Commodity price Index': ('PPICMM', False, 0.0750, 0.6518),
        'Capacity utilization': ('CUMFNS', False, 0.1328, 0.7533),
        'Personal consumption': ('DPCERA3M086SBEA', False, 0.0535, 0.1076),
        'Durable consumption': ('DDURRG3M086SBEA', False, 0.0850, 0.0616),
        'Non-durable cons.': ('DNDGRG3M086SBEA', False, 0.0327, 0.0621),
        'Unemployment': ('UNRATE', False, 0.1263, 0.8168),
        'Employment': ('PAYEMS', False, 0.0934, 0.7073),
        'Aver. Hourly Earnings': ('CES0600000008', False, 0.0965, 0.0721),
        'Housing Starts': ('HOUST', False, 0.0816, 0.3872),
        'New Orders': ('AMDMNOx', False, 0.1291, 0.6236),
        'S&P dividend yield': ('S&P div yield', False, 0.1136, 0.5486),
        'Consumer Expectations': ('UMCSENTx', False, 0.0514, 0.7005)
    }
    
    results = []
    
    for name, (col, is_y, original_vd, original_r2) in table_mapping.items():
        if is_y:
            r2 = 1.0000
            lam = np.array([0.0, 0.0, 0.0, 1.0])
        else:
            if col not in X.columns:
                # Si no está en X por limpieza, le asignamos valores NaN o aproximados
                results.append({
                    'Variable': name,
                    'col': col,
                    'Original_VD': original_vd,
                    'Original_R2': original_r2,
                    'Replica_VD': None,
                    'Replica_R2': None
                })
                continue
            idx = X.columns.get_loc(col)
            lam = Lambda[idx]
            
            # Calcular R^2 empírico
            reg = LinearRegression()
            F_and_Y = np.hstack([model.factors, Y.values.reshape(-1, 1)])
            reg.fit(F_and_Y, X[col].values)
            r2 = reg.score(F_and_Y, X[col].values)
            
        # FEVD
        num = 0.0
        den = 0.0
        policy_shock_idx = n_vars - 1
        
        for j in range(periods):
            lam_psi_j = np.dot(lam, Psi[j])
            num += lam_psi_j[policy_shock_idx] ** 2
            den += np.sum(lam_psi_j ** 2)
            
        vd = num / den if den > 0 else 0.0
        
        results.append({
            'Variable': name,
            'col': col,
            'Original_VD': original_vd,
            'Original_R2': original_r2,
            'Replica_VD': round(vd, 4),
            'Replica_R2': round(r2, 4)
        })
        
    # Guardar en un JSON en processed_data
    os.makedirs('processed_data', exist_ok=True)
    with open('processed_data/tabla_varianza_comparativa.json', 'w') as f:
        json.dump(results, f, indent=4)
        
    print("[✔] Tabla de varianza comparativa guardada exitosamente en processed_data/tabla_varianza_comparativa.json")

if __name__ == "__main__":
    main()
