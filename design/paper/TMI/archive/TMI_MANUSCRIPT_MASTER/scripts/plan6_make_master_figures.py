"""Render dense P6-E01 and P6-E11 master-manuscript figures."""
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np,pandas as pd
HERE=Path(__file__).resolve();MASTER=HERE.parents[1];EXP=MASTER/'experiments';FIG=MASTER/'figures';FIG.mkdir(parents=True,exist_ok=True)

# Metric robustness: point differences and clustered intervals.
x=pd.read_csv(EXP/'p6_e01_metric_robustness_summary.csv');datasets=['fastmri','ixi','ningxia'];models=['hat','swinir'];eps=['mae','rmse','mse','ssim_error','gradient_mae','lowfreq_mae','highfreq_mae'];labels=['MAE','RMSE','MSE','1−SSIM','Gradient','Low freq.','High freq.']
fig,axs=plt.subplots(2,3,figsize=(10.8,5.4),sharex=True)
for row,m in enumerate(models):
 for col,ds in enumerate(datasets):
  ax=axs[row,col];q=x[(x.dataset==ds)&(x.model==m)].set_index('endpoint').loc[eps].reset_index();y=np.arange(len(q))[::-1]
  ax.errorbar(q.delta_disjoint_minus_shared,y,xerr=[q.delta_disjoint_minus_shared-q.cluster_ci_low,q.cluster_ci_high-q.delta_disjoint_minus_shared],fmt='o',color='#235f9d',capsize=2,lw=1.1,ms=4);ax.axvline(0,color='.35',ls='--',lw=.8);ax.grid(axis='x',alpha=.2);ax.set_title(f'{ds} · {m.upper()}',fontsize=9);ax.set_yticks(y);ax.set_yticklabels(labels if col==0 else [],fontsize=8);ax.set_xlabel(r'$\rho_{disjoint}-\rho_{shared}$',fontsize=8)
fig.suptitle('Measurement-disjoint reliability is broad but not metric-independent',fontsize=11);fig.tight_layout();fig.savefig(FIG/'p6_e01_metric_robustness.pdf',bbox_inches='tight');fig.savefig(FIG/'p6_e01_metric_robustness.png',dpi=300,bbox_inches='tight');plt.close(fig)

# Factor robustness: normalized error plus decomposition/ranking.
s=pd.read_csv(EXP/'p6_e11_analytic_factor_summary.csv');fig,axs=plt.subplots(1,4,figsize=(12.0,3.1));colors={'fastmri':'#235f9d','ixi':'#4b9a57','ningxia':'#cf5b3f'}
metrics=[('pair_mae_mean','Pair MAE (relative to x2)',True),('shared_fraction_mean','Shared error fraction',False),('observable_fraction_mean','Observable fraction',False),('reliability_rho',r'Disagreement–error $\rho$',False)]
for ax,(metric,title,relative) in zip(axs,metrics):
 for ds,g in s.groupby('dataset'):
  g=g.sort_values('factor');y=g[metric].to_numpy();y=y/y[0] if relative else y;ax.plot(g.factor,y,'o-',lw=1.6,ms=4,color=colors[ds],label=ds)
 ax.set_xticks([2,4,6]);ax.set_xlabel('Interpolation factor');ax.set_title(title,fontsize=9);ax.grid(alpha=.2)
axs[0].set_ylabel('Value');axs[0].legend(frameon=False,fontsize=7);fig.suptitle('Larger missing-slice factors amplify consensus blindness',fontsize=11);fig.tight_layout();fig.savefig(FIG/'p6_e11_factor_robustness.pdf',bbox_inches='tight');fig.savefig(FIG/'p6_e11_factor_robustness.png',dpi=300,bbox_inches='tight');plt.close(fig)
print('Rendered',FIG/'p6_e01_metric_robustness.pdf',FIG/'p6_e11_factor_robustness.pdf')
