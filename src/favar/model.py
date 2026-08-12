import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.api import VAR

class FAVAR:
    """
    Implementación del modelo Factor-Augmented Vector Autoregressive (FAVAR)
    siguiendo la metodología de dos pasos de Bernanke, Boivin y Eliasz (2005).
    """
    def __init__(self, n_factors=3, lags=13):
        """
        n_factors: Número de factores latentes a extraer de X (K)
        lags: Número de rezagos en la especificación del VAR (BBE usan 13 rezagos para series mensuales)
        """
        self.n_factors = n_factors
        self.lags = lags
        
        # Atributos que se inicializarán en fit
        self.X_names = None
        self.Y_name = None
        self.factors = None
        self.loading_f = None
        self.loading_y = None
        self.var_result = None
        self.Z = None
        self.beta_coefs = None
        
    def fit(self, X, Y, fast_moving_cols):
        """
        Ajusta el modelo FAVAR de dos pasos:
        X: DataFrame de variables macroeconómicas estandarizadas (T x N)
        Y: Serie o DataFrame de la variable de política monetaria (T x 1, típicamente FEDFUNDS)
        fast_moving_cols: Lista de nombres de columnas en X que se consideran variables financieras/rápidas
        """
        self.X_names = list(X.columns)
        self.Y_name = Y.name if isinstance(Y, pd.Series) else Y.columns[0]
        
        # Alinear fechas
        common_idx = X.index.intersection(Y.index)
        X_df = X.loc[common_idx].copy()
        Y_val = Y.loc[common_idx].values.reshape(-1, 1)
        
        # 1. Identificar columnas lentas y rápidas en X
        slow_moving_cols = [c for c in self.X_names if c not in fast_moving_cols]
        X_slow = X_df[slow_moving_cols].copy()
        
        # 2. Extraer Componentes Principales de X completo (C_t)
        pca_all = PCA(n_components=self.n_factors)
        C_t = pca_all.fit_transform(X_df)
        
        # 3. Extraer Componentes Principales de X_slow (F_slow)
        pca_slow = PCA(n_components=self.n_factors)
        F_slow = pca_slow.fit_transform(X_slow)
        
        # 4. Limpiar los factores (eliminar la influencia de Y_t en C_t)
        # Regresamos C_t sobre F_slow e Y_val:
        # C_t = alpha * F_slow + beta * Y_val + e_t
        reg_data = np.hstack([F_slow, Y_val])
        reg = LinearRegression()
        reg.fit(reg_data, C_t)
        
        # El factor latente limpio F_t es la porción de C_t no explicada por Y_t (FEDFUNDS)
        # F_t = C_t - beta * Y_val
        beta = reg.coef_[:, self.n_factors:] # Coeficientes correspondientes a Y_val
        F_t = C_t - Y_val @ beta.T
        
        # Guardar factores como DataFrame
        factor_cols = [f"Factor_{i+1}" for i in range(self.n_factors)]
        self.factors = pd.DataFrame(F_t, index=common_idx, columns=factor_cols)
        
        # 5. Formar la matriz Z_t = [F_t, Y_t]
        self.Z = pd.concat([self.factors, pd.DataFrame(Y_val, index=common_idx, columns=[self.Y_name])], axis=1)
        
        # 6. Estimar el VAR sobre Z_t
        var_model = VAR(self.Z)
        self.var_result = var_model.fit(maxlags=self.lags, ic=None)
        print(f"[✔] VAR estimado sobre Z_t con {self.lags} rezagos.")
        print(self.var_result.summary())
        
        # 7. Obtener la matriz de cargas factoriales (factor loadings) de X sobre F_t e Y_t
        # Estimamos por mínimos cuadrados ordinarios (OLS) para cada variable j en X:
        # X_jt = lambda_f * F_t + lambda_y * Y_t + e_jt
        reg_loadings = LinearRegression()
        reg_loadings.fit(self.Z.values, X_df.values)
        
        self.loading_f = pd.DataFrame(reg_loadings.coef_[:, :self.n_factors], index=self.X_names, columns=factor_cols)
        self.loading_y = pd.Series(reg_loadings.coef_[:, self.n_factors], index=self.X_names, name=self.Y_name)
        
        print("[✔] Cargas factoriales estimadas para todas las variables de X.")
        
    def compute_irf(self, periods=48, impulse_size=1.0):
        """
        Calcula las funciones de impulso-respuesta (IRF) del VAR utilizando la
        identificación recursiva de Cholesky. Dado que Y_t se ordena al final de Z_t,
        el choque de política monetaria en Y_t no afecta contemporáneamente a F_t.
        """
        if self.var_result is None:
            raise ValueError("El modelo debe ajustarse (fit) antes de calcular las IRFs.")
            
        # Calcular las IRFs del VAR Z_t (F_t y Y_t)
        # statsmodels ordena por la estructura de la matriz Z
        irf_result = self.var_result.irf(periods=periods)
        
        # Obtener la matriz Cholesky de covarianza de residuos (P)
        sigma = self.var_result.sigma_u
        P = np.linalg.cholesky(sigma)
        
        # El choque en la variable de política (FEDFUNDS) está en la última columna/fila
        # Para un choque de 1 desviación estándar o un tamaño específico (ej: 25 puntos base)
        # Normalizamos la columna correspondiente del choque
        shock_idx = self.Z.shape[1] - 1
        
        # Matriz de respuestas ortogonalizadas del VAR
        # statsmodels.irf usa Cholesky directamente en irfs: irf_result.orth_irfs
        # Obtenemos las respuestas al choque en el último regresor (FEDFUNDS)
        # Dimensiones: (periods + 1, K + 1, K + 1)
        # Queremos las respuestas de todas las variables en Z ante un choque en la última variable (shock_idx)
        var_irfs = irf_result.orth_irfs[:, :, shock_idx] * impulse_size
        
        # Guardar en un DataFrame
        irf_df = pd.DataFrame(var_irfs, columns=self.Z.columns)
        return irf_df
        
    def get_macro_variable_irf(self, var_name, var_irfs_df):
        """
        Proyecta la respuesta del VAR sobre una variable macroeconómica individual de X:
        IRF_j,h = lambda_j_f * IRF_F,h + lambda_j_y * IRF_Y,h
        """
        if var_name not in self.X_names:
            raise ValueError(f"Variable {var_name} no encontrada en el panel macroeconómico original X.")
            
        # Extraer cargas
        lamb_f = self.loading_f.loc[var_name].values
        lamb_y = self.loading_y.loc[var_name]
        
        # Extraer IRFs de los factores (F) y de la tasa (Y)
        irf_factors = var_irfs_df[self.factors.columns].values
        irf_y = var_irfs_df[self.Y_name].values
        
        # Respuesta proyectada
        projected_irf = irf_factors @ lamb_f + irf_y * lamb_y
        return projected_irf
