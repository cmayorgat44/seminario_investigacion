import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.favar.data_loader import download_fred_md, load_and_clean_fred_md
from src.favar.model import FAVAR

# Ensure output directory exists
out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'docs', 'images'))
os.makedirs(out_dir, exist_ok=True)

# 1. Load Data
raw_path = download_fred_md()
X, Y, codes = load_and_clean_fred_md(raw_path, start_date='1959-01-01', end_date='2001-08-01')

# Ensure we have df to define fast_moving_cols correctly
df = X.copy()
df[Y.name] = Y

# Fast-moving variables (prices, aggregates) vs Slow-moving (production, employment)
fast_moving_prefixes = ['W875RX1', 'DPCERA3M086SBEA', 'CMRMTSPLx', 'RETAILx', 
                        'M2SL', 'M2REAL', 'AMBSL', 'TOTRESNS', 'NONBORRES', 
                        'BUSLOANS', 'REALLN', 'NONREVSL', 'CONSPI', 'S&P 500', 
                        'S&P: indust', 'S&P div yield', 'S&P PE ratio', 
                        'FEDFUNDS', 'CP3Mx', 'TB3MS', 'TB6MS', 'GS1', 'GS5', 'GS10', 
                        'AAA', 'BAA', 'COMPAPFFx', 'TB3SMFFM', 'TB6SMFFM', 'GS1MFFM', 
                        'GS5MFFM', 'GS10MFFM', 'AAAMFFM', 'BAAMFFM', 'TWEXAFEGSMTHx', 
                        'EXSZUSx', 'EXJPUSx', 'EXUSUKx', 'EXCAUSx', 'WPSFD49207', 
                        'WPSFD49502', 'WPSID61', 'WPSID62', 'OILPRICEx', 'PPICMM', 
                        'CPIAUCSL', 'CPIAPPSL', 'CPITRNSL', 'CPIMEDSL', 'CUSR0000SAC', 
                        'CUSR0000SAD', 'CUSR0000SAS', 'CPIULFSL', 'CUSR0000SA0L2', 
                        'CUSR0000SA0L5', 'PCEPI', 'DDURRG3M086SBEA', 'DNDGRG3M086SBEA', 
                        'DSERRG3M086SBEA']
fast_moving_cols = [c for c in df.columns if c in fast_moving_prefixes]

# X and Y are already extracted
fast_moving_cols = [c for c in X.columns if c in fast_moving_prefixes]

# 2. Fit FAVAR
favar = FAVAR(n_factors=3, lags=13)
favar.fit(X, Y, fast_moving_cols)

# 3. Compute IRFs
irf_df = favar.compute_irf(periods=48, impulse_size=0.25)

# 4. Plot Figure 3: Responses of latent factors
sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
factors = ['Factor_1', 'Factor_2', 'Factor_3']

for i, factor in enumerate(factors):
    axes[i].plot(irf_df.index, irf_df[factor], color='navy', linewidth=2)
    axes[i].axhline(0, color='black', linestyle='--', linewidth=1)
    axes[i].set_title(f'Response of {factor}')
    axes[i].set_xlabel('Months')

plt.tight_layout()
plt.savefig(os.path.join(out_dir, 'favar_fig3_factors.png'), dpi=300, bbox_inches='tight')
print(f"Saved {os.path.join(out_dir, 'favar_fig3_factors.png')}")

# 5. Extract Policy Shock (Figure 1 proxy)
# The policy shock in the VAR is the structural residual of FEDFUNDS.
sigma = favar.var_result.sigma_u
P = np.linalg.cholesky(sigma)
inv_P = np.linalg.inv(P)

# Structural residuals: e_t = P^-1 * u_t
residuals = favar.var_result.resid # (T-p, K+1)
structural_residuals = residuals @ inv_P.T

# The last column is the policy shock
policy_shock = structural_residuals.iloc[:, -1]

plt.figure(figsize=(10, 5))
plt.plot(policy_shock.index, policy_shock, color='darkred', linewidth=1)
plt.axhline(0, color='black', linewidth=1)
plt.title('Estimated Policy Shock (FAVAR)')
plt.ylabel('Standard Deviations')
plt.tight_layout()
plt.savefig(os.path.join(out_dir, 'favar_fig1_shock.png'), dpi=300, bbox_inches='tight')
print(f"Saved {os.path.join(out_dir, 'favar_fig1_shock.png')}")

