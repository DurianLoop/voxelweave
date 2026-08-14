"""Publication-quality diagnostic figures for Plan5+ CVPR upgrade evidence."""
from pathlib import Path
import json
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyBboxPatch

UP=Path(__file__).resolve().parents[1];OUT=UP/'outputs';FIG=UP/'figures';FIG.mkdir(exist_ok=True)
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':180})
def main():
 # Mechanism-to-method overview used as the paper's visual thesis.
 fig,ax=plt.subplots(figsize=(10.0,2.25));ax.set_xlim(0,10);ax.set_ylim(0,2.25);ax.axis('off')
 boxes=[(.15,'Shared physical\nmeasurements','#dceef2'),(2.65,'Aligned / common-mode\nreconstruction error','#e8e1ee'),(5.15,'Low disagreement despite\nhigh target error','#f8ead2'),(7.65,'Withhold an acquired anchor:\nAnchor-CV residual','#dfead9')]
 for x0,label,color in boxes:
  ax.add_patch(FancyBboxPatch((x0,.55),2.15,1.15,boxstyle='round,pad=.04,rounding_size=.08',facecolor=color,edgecolor='#374151',linewidth=1.0));ax.text(x0+1.075,1.125,label,ha='center',va='center',fontsize=10)
 for x0 in [2.38,4.88,7.38]: ax.annotate('',xy=(x0+.2,1.125),xytext=(x0-.1,1.125),arrowprops=dict(arrowstyle='-|>',lw=1.2,color='#374151'))
 ax.text(3.75,.23,'Shared influence quantifies the mechanism',ha='center',fontsize=9,color='#754668');ax.text(8.73,.23,'Cross-validation creates a measured pseudo-target',ha='center',fontsize=9,color='#147d92')
 fig.tight_layout(pad=.2);fig.savefig(FIG/'fig_mechanism_overview.pdf',bbox_inches='tight');fig.savefig(FIG/'fig_mechanism_overview.png',bbox_inches='tight');plt.close(fig)
 # Method correlations.
 s=json.loads((OUT/'anchor_cross_validation_summary.json').read_text())['rows'];a=json.loads((OUT/'analytical_acquired_anchor_bipartition_summary.json').read_text())['rows'];sa={q['dataset']:q for q in s};aa={q['dataset']:q for q in a};ds=['fastmri','ixi','ningxia'];labels=['fastMRI','IXI','NingXia'];x=range(3)
 fig,ax=plt.subplots(figsize=(5.8,3.2));ax.bar([q-.18 for q in x],[sa[d]['rho_score_vs_x4_error'] for d in ds],.36,label='Anchor CV',color='#147d92');ax.bar([q+.18 for q in x],[aa[d]['rho_score_vs_x4_error'] for d in ds],.36,label='Bipartition',color='#e59f3a');ax.set_xticks(list(x),labels);ax.set_ylim(.7,1);ax.set_ylabel('Spearman with x4 error');ax.legend(frameon=False,ncol=2);fig.tight_layout();fig.savefig(FIG/'fig_anchor_cv_comparison.pdf');fig.savefig(FIG/'fig_anchor_cv_comparison.png');plt.close(fig)
 # Budget curves.
 b=pd.read_csv(OUT/'anchor_cv_comparison_budgets.csv');fig,axs=plt.subplots(1,2,figsize=(7,3),sharey=True)
 for ax,d,title in zip(axs,['fastmri','ningxia'],['fastMRI','NingXia']):
  q=b[b.dataset.eq(d)]
  for method,name,color in [('score','Anchor CV','#147d92'),('bipartition_score','Bipartition','#e59f3a'),('phase_grid_score','Extra-grid score','#754668'),('input_adj_rmse','Adjacent RMSE','#6b7280')]:
   z=q[q.method.eq(method)];ax.plot(z.budget*100,z.fraction_oracle_above_random,marker='o',label=name,color=color)
  ax.axhline(0,color='k',lw=.6);ax.set_title(title);ax.set_xlabel('Densification budget (%)');ax.set_ylim(-.05,1.08)
 axs[0].set_ylabel('Fraction of oracle gain above random');axs[1].legend(frameon=False,fontsize=7);fig.tight_layout();fig.savefig(FIG/'fig_anchor_cv_budget.pdf');fig.savefig(FIG/'fig_anchor_cv_budget.png');plt.close(fig)
 if (OUT/'compact_four_anchor_overlap_ladder_summary.json').exists():
  z=json.loads((OUT/'compact_four_anchor_overlap_ladder_summary.json').read_text())['rows'];fig,axs=plt.subplots(1,3,figsize=(8.2,2.8),sharex=True)
  for rec,color in zip(z,['#147d92','#e59f3a','#754668']):
   l=rec['levels'];ov=[q['overlap'] for q in l];axs[0].plot(ov,[q['error_cosine_mean'] for q in l],'-o',label=rec['dataset'],color=color);axs[1].plot(ov,[q['observable_fraction_mean'] for q in l],'-o',color=color);axs[2].plot(ov,[q['disagreement_mae_mean'] for q in l],'-o',color=color)
  for ax in axs:ax.set_xticks(range(5));ax.set_xlabel('Shared anchors (of 4)')
  axs[0].set_ylabel('Error cosine');axs[1].set_ylabel('Observable fraction');axs[2].set_ylabel('Disagreement MAE');axs[0].legend(frameon=False);fig.tight_layout();fig.savefig(FIG/'fig_compact_overlap_ladder.pdf');fig.savefig(FIG/'fig_compact_overlap_ladder.png');plt.close(fig)
 # Show all configurations for the refined shared-influence mechanism.
 if (OUT/'shared_influence_per_case_config.csv').exists():
  z=pd.read_csv(OUT/'shared_influence_per_case_config.csv')
  g=z.groupby(['dataset','config_id'],as_index=False).agg(common_abs_mass=('common_abs_mass','first'),error_cosine=('error_cosine','mean'),observable_fraction=('observable_fraction','mean'))
  fig,axs=plt.subplots(1,2,figsize=(7.1,3.0))
  colors={'fastmri':'#147d92','ixi':'#e59f3a','ningxia':'#754668'}; names={'fastmri':'fastMRI','ixi':'IXI','ningxia':'NingXia'}
  for d in ['fastmri','ixi','ningxia']:
   q=g[g.dataset.eq(d)];axs[0].scatter(q.common_abs_mass,q.error_cosine,s=24,alpha=.82,label=names[d],color=colors[d]);axs[1].scatter(q.common_abs_mass,q.observable_fraction,s=24,alpha=.82,color=colors[d])
  axs[0].set_ylabel('Error cosine');axs[1].set_ylabel('Observable error fraction')
  for ax in axs: ax.set_xlabel('Common absolute coefficient mass')
  axs[0].legend(frameon=False,fontsize=8);fig.tight_layout();fig.savefig(FIG/'fig_shared_influence.pdf');fig.savefig(FIG/'fig_shared_influence.png');plt.close(fig)
if __name__=='__main__':main()
