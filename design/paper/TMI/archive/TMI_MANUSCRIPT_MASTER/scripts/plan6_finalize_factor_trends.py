"""Rebuild the small P6-E11 trend table from the completed summary."""
from pathlib import Path
import pandas as pd
from scipy import stats
OUT=Path(__file__).resolve().parents[1]/'experiments';s=pd.read_csv(OUT/'p6_e11_analytic_factor_summary.csv');rows=[]
for ds,g in s.groupby('dataset'):
 for metric in ['pair_mae_mean','shared_fraction_mean','observable_fraction_mean','disagreement_mae_mean','reliability_rho']:
  rows.append({'dataset':ds,'metric':metric,'spearman_vs_factor':float(stats.spearmanr(g['factor'],g[metric]).statistic),**{f'x{f}':float(g.loc[g['factor']==f,metric].iloc[0]) for f in (2,4,6)}})
pd.DataFrame(rows).to_csv(OUT/'p6_e11_analytic_factor_trends.csv',index=False);print(pd.DataFrame(rows).to_string(index=False))
