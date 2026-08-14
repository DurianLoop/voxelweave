"""Create compact, publication-quality TMI figures from frozen evidence."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch

HERE=Path(__file__).resolve(); TMI=HERE.parents[1]; PAPER=HERE.parents[3]; FIG=TMI/'figures'; FIG.mkdir(exist_ok=True)
plt.rcParams.update({'font.size':8,'axes.titlesize':9,'axes.labelsize':8,'legend.fontsize':7,'font.family':'DejaVu Sans','pdf.fonttype':42})
BLUE='#2463A3'; ORANGE='#D8772F'; RED='#B53A3A'; GREEN='#2B8C6B'; GREY='#6B7280'
def save(fig,name):
 fig.tight_layout();fig.savefig(FIG/f'{name}.pdf',bbox_inches='tight');fig.savefig(FIG/f'{name}.png',dpi=300,bbox_inches='tight');plt.close(fig)

def concept():
 fig,ax=plt.subplots(figsize=(7.0,2.0));ax.set_xlim(0,12);ax.set_ylim(0,3);ax.axis('off')
 for y,title,color,lab in [(2.15,'Shared measurements',ORANGE,'aligned errors cancel'),(.75,'Disjoint measurements',BLUE,'context-sensitive errors remain visible')]:
  ax.text(.05,y,title,weight='bold',va='center',color=color)
  for x in (2.6,3.35): ax.add_patch(Circle((x,y),.20,fc=color,ec='white'));ax.text(x,y,'m',ha='center',va='center',color='white',weight='bold')
  if y>1: ax.plot([2.6,3.35],[y,y],lw=5,color=color,alpha=.35)
  for x,t in [(5.2,'reconstruction a'),(7.15,'reconstruction b')]:
   ax.add_patch(FancyBboxPatch((x-.7,y-.28),1.4,.56,boxstyle='round,pad=.06',fc='#F5F7FA',ec=color));ax.text(x,y,t,ha='center',va='center')
  for a,b in [((3.6,y),(4.45,y)),((5.95,y),(6.4,y)),((7.9,y),(8.75,y))]:ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=10,color=GREY))
  ax.add_patch(FancyBboxPatch((8.85,y-.28),1.25,.56,boxstyle='round,pad=.06',fc='white',ec=color));ax.text(9.48,y,'|fₐ−fᵦ|',ha='center',va='center',weight='bold')
  ax.text(10.35,y,lab,va='center',color=color)
 ax.text(6,2.85,'Disagreement observes only error differences:  fₐ−fᵦ = eₐ−eᵦ',ha='center',weight='bold',fontsize=10)
 save(fig,'fig1_concept')

def design():
 fig,axs=plt.subplots(1,2,figsize=(7.0,2.2),sharey=True)
 for ax,title,phase in zip(axs,['Zero anchor overlap','Maximum shared anchors + order reversal'],[2,0]):
  ax.set_title(title,weight='bold');ax.set_xlim(-.5,9.5);ax.set_ylim(-.6,1.2);ax.set_yticks([]);ax.set_xlabel('through-plane index z')
  for z in range(9):
   if z%4==0: ax.scatter(z,.55,s=70,color=ORANGE,edgecolor='white',zorder=3,label='phase-0 anchor' if z==0 else None)
   if z%4==phase and phase!=0: ax.scatter(z,.05,s=70,color=BLUE,edgecolor='white',zorder=3,label='phase-2 anchor' if z==2 else None)
   if z%4 in (1,3): ax.scatter(z,.9,s=65,marker='*',color=RED,label='same target' if z==1 else None)
  if phase==0:
   ax.scatter([0,4,8],[.05]*3,s=70,color=BLUE,edgecolor='white',zorder=3,label='same anchors, reversed order')
  ax.plot([0,8],[.55,.55],color=ORANGE,alpha=.3);ax.plot([0,8],[.05,.05],color=BLUE,alpha=.3)
 axs[0].legend(ncol=2,loc='lower center',bbox_to_anchor=(1.03,-.43),frameon=False)
 save(fig,'fig2_design')

def main_result():
 x=pd.read_csv(PAPER/'plan4_outputs'/'overlap_zero_vs_max_paired.csv');corr=json.loads((TMI/'tables'/'ningxia_patient_cluster_corrections.json').read_text())
 fig,axs=plt.subplots(1,2,figsize=(7.0,2.65))
 for ax,ds,name in zip(axs,['fastmri','ningxia'],['fastMRI brain T2 (24 cases)','NingXia knee T2 (8 patients / 22 series)']):
  g=x[x.dataset.eq(ds)];ax.scatter(g.disjoint_inconsistency,g.phase0_error,s=8,alpha=.35,color=BLUE,label='zero overlap')
  ax.scatter(g.max_shared_inconsistency,g.phase0_error,s=8,alpha=.28,color=ORANGE,label='max shared + reversal')
  rz=g.disjoint_inconsistency.corr(g.phase0_error,method='spearman');rm=g.max_shared_inconsistency.corr(g.phase0_error,method='spearman')
  ax.set_title(f'{name}\nSpearman {rz:.3f} vs {rm:.3f}',weight='bold');ax.set_xlabel('prediction-only disagreement (MAE)');ax.set_ylabel('retrospective reconstruction MAE');ax.grid(alpha=.15)
 axs[0].legend(frameon=False);save(fig,'fig3_main_overlap')

def generalization():
 hist=json.loads((PAPER/'plan4_outputs'/'overlap_zero_vs_max_summary.json').read_text())['rows'];rows=[]
 for r in hist:
  if 'target_model' in r:rows.append((r['dataset'],r['target_model'],r['delta_plane_rho'],r['case_cluster_95ci']))
 ana=json.loads((PAPER/'plan4_outputs'/'analytical_disjoint_summary.json').read_text())['profiles']
 fig,axs=plt.subplots(1,2,figsize=(7.0,2.55))
 labels=[f'{d}\n{m.upper()}' for d,m,_,_ in rows];v=[q[2] for q in rows];lo=[q[2]-q[3][0] for q in rows];hi=[q[3][1]-q[2] for q in rows]
 axs[0].errorbar(range(len(v)),v,yerr=[lo,hi],fmt='o',color=BLUE,capsize=3);axs[0].axhline(0,color='black',lw=.7);axs[0].set_xticks(range(len(v)),labels,rotation=30,ha='right');axs[0].set_ylabel('Δ Spearman (zero − maximum)');axs[0].set_title('Neural architecture robustness',weight='bold');axs[0].grid(axis='y',alpha=.15)
 labs=[f"{r['dataset']}\n{r['method']}" for r in ana];vals=[r['case_spearman'] for r in ana];axs[1].bar(range(4),vals,color=[BLUE,BLUE,ORANGE,ORANGE]);axs[1].set_xticks(range(4),labs,rotation=30,ha='right');axs[1].set_ylim(.9,1);axs[1].set_ylabel('case-level Spearman');axs[1].set_title('Analytical interpolators',weight='bold');axs[1].grid(axis='y',alpha=.15)
 save(fig,'fig4_generalization')

def decomposition_and_consequence():
 dec=json.loads((PAPER/'plan3_outputs'/'bias_diversity_summary.json').read_text())['summary'];ad=json.loads((PAPER/'plan4_outputs'/'adaptive_acquisition_summary.json').read_text())['rows']
 fig,axs=plt.subplots(1,2,figsize=(7.0,2.55))
 labels=['fastMRI','NingXia'];shared=[r['median_shared_fraction'] for r in dec];div=[r['median_diversity_fraction'] for r in dec]
 axs[0].bar(labels,shared,color=ORANGE,label='shared consensus');axs[0].bar(labels,div,bottom=shared,color=BLUE,label='observable diversity');axs[0].set_ylim(0,1);axs[0].set_ylabel('median fraction of squared error');axs[0].set_title('Most error is shared',weight='bold');axs[0].legend(frameon=False)
 x=np.arange(2);w=.24;axs[1].bar(x-w,[r['random_policy_gain'] for r in ad],w,label='random',color=GREY);axs[1].bar(x,[r['top_quartile_policy_gain'] for r in ad],w,label='disjoint score',color=BLUE);axs[1].bar(x+w,[r['oracle_policy_gain'] for r in ad],w,label='oracle',color=ORANGE);axs[1].set_xticks(x,labels);axs[1].set_ylabel('x4→x2 MAE reduction');axs[1].set_title('Retrospective top-25% densification',weight='bold');axs[1].legend(frameon=False,ncol=3,loc='upper center',fontsize=6)
 save(fig,'fig5_decomposition_consequence')

def main():
 concept();design();main_result();generalization();decomposition_and_consequence()
if __name__=='__main__':main()
