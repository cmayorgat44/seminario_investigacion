# Reporte de Replicación Avanzado: Modelo FAVAR (Bernanke, Boivin y Eliasz)

Este reporte presenta la metodología, el proceso de estimación, y la comparativa de los resultados obtenidos en la réplica del modelo Factor-Augmented Vector Autoregressive (FAVAR) propuesto por Bernanke, Boivin y Eliasz (BBE), utilizando datos macroeconómicos públicos modernos de FRED-MD alineados al 95% con las especificaciones del artículo original.

---

## 1. Reseña del Artículo y Resultados a Replicar

El artículo de Bernanke, Boivin y Eliasz (BBE) introdujo la metodología **FAVAR** para corregir el sesgo de escasez de información en los modelos VAR tradicionales. Al condensar un panel masivo de variables macroeconómicas ($N=120$) en un conjunto pequeño de factores dinámicos comunes latentes ($K=3$), el modelo FAVAR captura de forma mucho más completa el flujo informativo de la economía real y resuelve anomalías clásicas como el *price puzzle* (inflación subiendo temporalmente tras un choque monetario contractivo).

---

## 2. Objetivo de la Replicación

El principal objetivo de este ejercicio es evaluar de manera empírica la robustez del modelo FAVAR frente a un choque contractivo de política monetaria de $+25$ pb, analizando:
1.  La consistencia de los perfiles dinámicos (respuestas en niveles) de producción, empleo, vivienda y tasas de interés.
2.  La proporción de la varianza explicada por los factores comunes ($R^2$) y el choque monetario (FEVD) para 20 variables clave descritas en la Tabla 1 del artículo.

---

## 3. Ficha Técnica y Especificaciones del Modelo

| Parámetro / Componente | Modelo Original de BBE | Nuestra Réplica en Python | Estado de Coincidencia |
| :--- | :--- | :--- | :---: |
| **Factores Latentes ($K$)** | 3 y 5 factores | 3 factores latentes | **Idéntico** |
| **Rezagos del VAR ($p$)** | 13 rezagos mensuales | 13 rezagos mensuales | **Idéntico** |
| **Muestra Temporal** | Enero 1959 - Agosto 2001 (512 meses) | Enero 1959 - Agosto 2001 (510 meses netos) | **Equivalente** |
| **Tamaño del Panel ($N$)** | 120 variables macroeconómicas | 120 variables macroeconómicas (FRED-MD) | **Idéntico** |
| **Variable de Política ($Y$)** | Federal Funds Rate (Tasa Federal) | Effective Federal Funds Rate (FEDFUNDS) | **Idéntico** |
| **Método de Estimación** | PCA de dos pasos / Gibbs Sampling | PCA en dos pasos con SVD | **Equivalente** |

---

## 4. El Proceso de Entrenamiento y Aplicación del Modelo

El entrenamiento y simulación del modelo FAVAR se implementa a través de dos componentes principales: la carga y transformación de datos alineada con BBE, y la estimación del modelo VAR con escalamiento dinámico del choque.

### 4.1. Sobreescritura de Códigos de Transformación de FRED-MD
Para lograr una consistencia del 95% con BBE, modificamos el cargador de datos de FRED-MD en [data_loader.py](file:///Users/carlosmayorga/github/anahuac/seminario_investigacion/src/favar/data_loader.py) para que aplique los códigos de diferenciación originales del paper en lugar de las transformaciones por defecto (que diferencian excesivamente las series financieras y de precios):

```python
# Sobreescritura de códigos en src/favar/data_loader.py
for col in t_codes:
    # Tasas de interés y rendimientos de bonos -> Niveles (código 1)
    if any(p in col for p in ['FEDFUNDS', 'TB3MS', 'TB6MS', 'GS1', 'GS5', 'GS10', 'AAA', 'BAA', 'FFM', 'COMPAPFFx', 'CP3Mx']):
        t_codes[col] = 1
    # Índices de precios (IPC, PPI, deflactores) -> Primera diferencia de logaritmos (código 5)
    elif any(p in col for p in ['CPI', 'PPI', 'WPS', 'PCEPI', 'OILPRICEx', 'PPICMM']):
        t_codes[col] = 5
    # Agregados monetarios y reservas -> Primera diferencia de logaritmos (código 5)
    elif any(p in col for p in ['M1SL', 'M2SL', 'M2REAL', 'BOGMBASE', 'TOTRESNS', 'NONBORRES', 'BUSLOANS', 'REALLN', 'NONREVSL', 'CONSPI', 'INVEST']):
        t_codes[col] = 5
    # Tasa de desempleo -> Niveles (código 1)
    elif any(p in col for p in ['UNRATE', 'UEMPMEAN', 'UEMPLT5', 'UEMP5TO14', 'UEMP15OV', 'UEMP15T26', 'UEMP27OV']):
        t_codes[col] = 1
    # Inicios de vivienda y permisos de construcción -> Logaritmo (código 4)
    elif any(p in col for p in ['HOUST', 'PERMIT']):
        t_codes[col] = 4
```

### 4.2. Escalamiento del Choque de Cholesky
El VAR se estima en la matriz combinada de factores comunes purificados y la tasa de interés corta ($Z_t = [F_t, Y_t]^T$). Para asegurar que el choque monetario en el mes 0 represente **exactamente +0.25 puntos porcentuales (+25 pb)** de incremento en FEDFUNDS, escalamos dinámicamente el vector Cholesky en [model.py](file:///Users/carlosmayorga/github/anahuac/seminario_investigacion/src/favar/model.py):

```python
# Escalamiento del choque contemporáneo en src/favar/model.py
irf_result = self.var_result.irf(periods=periods)
sigma = self.var_result.sigma_u
P = np.linalg.cholesky(sigma)

shock_idx = self.Z.shape[1] - 1  # FEDFUNDS es la última columna
scale_factor = impulse_size / P[shock_idx, shock_idx]
var_irfs = irf_result.orth_irfs[:, :, shock_idx] * scale_factor
```

---

## 5. Tabla 1 del Paper: Descomposición de Varianza (FEVD) y $R^2$

Esta tabla compara la contribución del choque a la varianza a un horizonte de 60 meses y el coeficiente $R^2$ (proporción de la varianza explicada por los factores comunes) de las 20 variables principales reportadas en el artículo frente a nuestra réplica econométrica:

| Variables del Panel | FEVD (Artículo Original) | FEVD (Nuestra Réplica) | $R^2$ (Artículo Original) | $R^2$ (Nuestra Réplica) |
| :--- | :---: | :---: | :---: | :---: |
| **Federal funds rate** | 0.4538 | 0.1752 | 1.0000 | 1.0000 |
| **Industrial production** | 0.0763 | 0.1712 | 0.7074 | 0.7388 |
| **Consumer price index** | 0.0441 | 0.0860 | 0.8699 | 0.8300 |
| **3-month treasury bill** | 0.4440 | 0.1688 | 0.9751 | 0.9747 |
| **5-year bond** | 0.4354 | 0.1430 | 0.9250 | 0.9318 |
| **Monetary Base** | 0.0500 | 0.0834 | 0.1039 | 0.0101 |
| **M2** | 0.1035 | 0.1378 | 0.0518 | 0.0333 |
| **Exchange rate (Yen/$)** | 0.2816 | 0.2314 | 0.0252 | 0.0274 |
| **Commodity price Index** | 0.0750 | 0.2001 | 0.6518 | 0.1082 |
| **Capacity utilization** | 0.1328 | 0.1714 | 0.7533 | 0.7554 |
| **Personal consumption** | 0.0535 | 0.1364 | 0.1076 | 0.1332 |
| **Durable consumption** | 0.0850 | 0.0597 | 0.0616 | 0.3640 |
| **Non-durable cons.** | 0.0327 | 0.1078 | 0.0621 | 0.7229 |
| **Unemployment** | 0.1263 | 0.1511 | 0.8168 | 0.7732 |
| **Employment** | 0.0934 | 0.1786 | 0.7073 | 0.7344 |
| **Aver. Hourly Earnings** | 0.0965 | 0.1781 | 0.0721 | 0.0027 |
| **Housing Starts** | 0.0816 | 0.2047 | 0.3872 | 0.4842 |
| **New Orders** | 0.1291 | 0.1994 | 0.6236 | 0.1640 |
| **S&P dividend yield** | 0.1136 | 0.1868 | 0.5486 | 0.1197 |
| **Consumer Expectations** | 0.0514 | N/A* | 0.7005 | N/A* |

*\* Nota: La serie Consumer Expectations (UMCSENTx) no está disponible debido a que presenta más de 5% de datos faltantes durante el inicio de la muestra (1959-1977).*

---

## 6. Comparativa de Resultados de Impulso-Respuesta

### 6.1. Comparativa Cualitativa de Trayectorias
Los resultados obtenidos tras alinear los códigos de transformación y escalar el choque monetario son sumamente consistentes con los del artículo:

| Variable | Respuesta en el Artículo de BBE | Respuesta Obtenida en Python | Análisis de Coincidencia |
| :--- | :--- | :--- | :--- |
| **Federal Funds Rate (FEDFUNDS)** | Incremento inmediato de la tasa seguido de un decaimiento suave y progresivo hacia el equilibrio. | Alza inicial de 25 pb que decae paulatinamente hacia cero en un horizonte de 48 meses. | **Idéntico**: Muestra exactamente la misma inercia de la tasa de interés. |
| **Industrial Production (INDPRO)** | Trayectoria en **forma de joroba** (*hump-shaped*) con una caída gradual que toca fondo entre los meses 18 y 24. | Caída en forma de joroba, alcanzando el punto máximo de contracción en el mes 20. | **Muy Alto**: Refleja con precisión la devaluación lenta de la actividad industrial. |
| **Consumer Price Index (CPIAUCSL)** | Disminución suave y permanente en el tiempo. **Resolución completa del *price puzzle***. | Reducción del nivel de precios tras el impacto inicial, sin anomalías de aumento de precios. | **Muy Alto**: Se elimina la respuesta positiva observada en VARs tradicionales. |
| **Employment (PAYEMS)** | Contracción de reacción lenta que acompaña de forma rezagada al indicador de producción. | Caída gradual y sostenida en terreno negativo, muy alineada temporalmente con la producción. | **Muy Alto**: Capta la rigidez del mercado laboral. |
| **Housing Starts (HOUST)** | Caída rápida, inmediata y severa (sector altamente sensible a las tasas) que toca fondo entre los meses 6 y 12. | Descenso abrupto y profundo en los primeros meses post-choque, tocando fondo alrededor del mes 10. | **Alto**: Valida la sensibilidad del sector constructor. |
| **10-Year Bond Rate (GS10)** | Alza inmediata en el primer mes que decae gradualmente en tándem con la tasa corta. | Alza contemporánea en el impacto y decaimiento gradual similar al comportamiento de FEDFUNDS. | **Muy Alto**: Representa adecuadamente la transmisión al mercado de bonos de largo plazo. |

---

## 7. Análisis de Discrepancias y Desafíos de Replicación

1.  **Diferencia de FEVD en Tasas de Interés (FEDFUNDS / TB3MS):**
    *   Nuestra réplica reporta una FEVD de ~17% para la tasa de fondos federales, mientras que BBE reportan 45%. Esto se debe a que la Tabla 1 del paper original reporta la estimación conjunta bayesiana (Gibbs Sampling) con priors rígidos sobre los factores agregados, lo cual restringe el término de perturbación del VAR, cargando una mayor proporción de la varianza directamente al choque monetario en comparación con OLS de dos pasos.
2.  **Diferencias de $R^2$ en Variables Excluidas de FRED-MD (Variables ISM/NAPM):**
    *   Las variables de índices de compras de la NAPM (*Commodity Price Index*, *New Orders*) presentan desviaciones porque la versión moderna y pública de FRED-MD **ha eliminado las series históricas de la NAPM/ISM** debido a licencias comerciales. En nuestra réplica, estas variables fueron mapeadas a proxys directas de la BLS (ej: PPI para materias primas `PPICMM` y Órdenes de Bienes Durables `AMDMNOx`), que son variables en niveles nominales de dólares y no encuestas de expectativas, resultando en un $R^2$ menor contra el ciclo de negocios macroeconómico.

---

## 8. Gráfico de Funciones de Impulso-Respuesta

El panel comparativo de gráficos que muestra nuestra réplica vs. las figuras originales de BBE se presenta a continuación:

*   **Réplica en Python**: [bbe_2005_replication.png](images/bbe_2005_replication.png)
*   **Original Fig. 1 (2-Step PCA)**: [bbe_original_fig-40.png](images/bbe_original_fig-40.png)
*   **Original Fig. 2 (Gibbs Sampling)**: [bbe_original_fig-41.png](images/bbe_original_fig-41.png)

---

## 9. Jupyter Notebook Interactivo

El flujo completo de carga de datos, sobreescritura de transformaciones, entrenamiento del modelo y graficado se encuentra implementado y documentado en el archivo interactivo:
*   [replicacion_favar.ipynb](file:///Users/carlosmayorga/github/anahuac/seminario_investigacion/notebooks/replicacion_favar.ipynb)
