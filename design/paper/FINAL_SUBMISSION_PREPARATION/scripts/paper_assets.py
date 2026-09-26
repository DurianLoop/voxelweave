"""Generate all main figures/tables from independently array-derived records."""
from common import PATCH as P,PAPER,ROOT,BASEOUT,OUT,MODELS,sha,write
import numpy as np,pandas as pd,importlib.util,shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=OUT/'array_reproduced';CV=P/'revised_manuscript';FIG=P/'figures'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
def save(fig,name):
 fig.savefig(FIG/(name+'.pdf'),bbox_inches='tight',pad_inches=.03);fig.savefig(FIG/(name+'.png'),dpi=200,bbox_inches='tight',pad_inches=.03);plt.close(fig);shutil.copy2(FIG/(name+'.pdf'),CV/(name+'.pdf'))
def controls():
 clean=pd.concat([pd.read_csv(R/'clean_max_overlap_per_plane.csv'),pd.read_csv(R/'clean_max_overlap_ixi_per_plane.csv')]);zero=pd.concat([pd.read_csv(R/'overlap_covariance_per_plane.csv'),pd.read_csv(R/'overlap_covariance_ixi_per_plane.csv')]);key=['dataset','case_id','patient_cluster','model','z']
 g=clean[key+['observable_fraction','score','error']].merge(zero[key+['observable_fraction','disagreement_mae','mae']],on=key,suffixes=('_s','_d'),validate='one_to_one');g['delta']=g.observable_fraction_d-g.observable_fraction_s
 # Uniform patient/examination weighting; neither planes nor series multiply independent units.
 unit=g.groupby(['dataset','patient_cluster','case_id','model'])[['observable_fraction_s','observable_fraction_d','delta']].mean().groupby(['dataset','patient_cluster','case_id']).mean().groupby(['dataset','patient_cluster']).mean();records=[]
 for ds,seed in [('fastmri',19003),('ixi',19004),('ningxia',19005)]:
  a=unit.loc[ds];values=a.to_numpy();idx=np.random.default_rng(seed).integers(0,len(a),(5000,len(a)));b=values[idx].mean(1);pt=values.mean(0);lo,hi=np.quantile(b,[.025,.975],axis=0)
  rec=dict(dataset=ds,units=len(a))
  for j,name in enumerate(['shared_O','disjoint_O','delta_O']):rec.update({name:pt[j],name+'_low':lo[j],name+'_high':hi[j]})
  records.append(rec)
 d=pd.DataFrame(records);d.to_csv(OUT/'revised_local_control.csv',index=False);unit.to_csv(OUT/'revised_local_control_per_unit.csv')
 fig,ax=plt.subplots(1,2,figsize=(7.05,2.25),gridspec_kw={'wspace':.35});y=np.arange(3)
 for off,col,name,label in [(-.13,'#af6425','shared_O','Shared'),(.13,'#236c98','disjoint_O','Disjoint')]:
  ax[0].errorbar(100*d[name],y+off,xerr=100*np.array([d[name]-d[name+'_low'],d[name+'_high']-d[name]]),fmt='o',color=col,capsize=2,label=label,ms=4)
 ax[0].set_yticks(y,['fastMRI','IXI','NingXia']);ax[0].invert_yaxis();ax[0].set_xlabel('Observable paired-error fraction (%)');ax[0].set_title('(a) Same-model local observability',fontsize=8,weight='bold');ax[0].legend(fontsize=7,frameon=False,loc='lower right');ax[0].grid(axis='x',color='.93')
 o=100*d.shared_O.to_numpy();ax[1].barh(y,100-o,color='#366e95',label='Common');ax[1].barh(y,o,left=100-o,color='#cf883c',label='Observable');ax[1].set_yticks(y,['fastMRI','IXI','NingXia']);ax[1].invert_yaxis();ax[1].set_xlim(0,112)
 for j,v in enumerate(o):ax[1].text(101,j,f'{v:.2f}%',va='center',fontsize=7)
 ax[1].set_xlabel('Shared paired-error energy (%)');ax[1].set_title('(b) Common error under sharing',fontsize=8,weight='bold');ax[1].legend(fontsize=7,frameon=False,loc='lower center',bbox_to_anchor=(.5,-.45),ncol=2)
 fig.subplots_adjust(left=.09,right=.99,bottom=.27,top=.85);save(fig,'final_fig2_original_control')
 rows=[]
 for v in d.itertuples():
  name={'fastmri':'fastMRI','ixi':'IXI','ningxia':'NingXia'}[v.dataset];rows.append(f'{name} & {v.units} & {100*v.shared_O:.2f} & {100*v.disjoint_O:.2f} & {100*v.delta_O:.2f} [{100*v.delta_O_low:.2f},{100*v.delta_O_high:.2f}] '+r'\\')
 text=r'''\begin{table}[t]\centering\small
\caption{Original clean same-model control, re-expressed with uniform local estimands. Target means, equal model means and patient/examination means; NingXia first averages series within patient. Pointwise 95\% paired cluster intervals. $O$ is in percent; $\Delta O$ in percentage points.}
\label{tab:controlled}\setlength{\tabcolsep}{3pt}
\begin{tabular}{lrrrr}\toprule Cohort & Units & Shared $O$ & Disjoint $O$ & $\Delta O$ [CI]\\\midrule
'''+ '\n'.join(rows)+r'\bottomrule\end{tabular}\end{table}'
 (CV/'local_control_table.tex').write_text(text,encoding='utf-8')
 # Preserve old pooled-plane ranking and stable-wrong in a dedicated supplement figure.
 old=pd.read_csv(OUT/'reproduced_original_control.csv').set_index('dataset').loc[d.dataset];flags=[]
 for ds in d.dataset:
  f=[]
  for _,q in g[g.dataset==ds].groupby('model'):
   e=q.mae.quantile(.75);s=q.disagreement_mae.quantile(.25);f.extend(((q.error>=e)&(q.score<=s)).astype(int)-((q.mae>=e)&(q.disagreement_mae<=s)).astype(int))
  flags.append(100*np.mean(f))
 fig,ax=plt.subplots(1,2,figsize=(7.05,2.2));ax[0].errorbar(old.delta,y,xerr=np.array([old.delta-old.low,old.high-old.delta]),fmt='o',color='#236c98',capsize=3);ax[0].axvline(0,color='.5',ls='--',lw=.7);ax[0].set_xlabel('Pooled-plane ranking change');ax[0].set_title('(a) Historical ranking',fontsize=8,weight='bold');ax[1].barh(y,flags,color='#9c6340');ax[1].set_xlabel('Shared − disjoint prevalence (pp)');ax[1].set_title('(b) Historical stable-wrong',fontsize=8,weight='bold')
 for a in ax:a.set_yticks(y,['fastMRI','IXI','NingXia']);a.invert_yaxis()
 fig.tight_layout();save(fig,'historical_ranking_prevalence');pd.DataFrame({'dataset':d.dataset,'stable_wrong_pp':flags}).to_csv(OUT/'historical_prevalence.csv',index=False)
def influence():
 d=pd.read_csv(R/'acquired_only_summary.csv');prop=pd.read_csv(R/'proposition_summary.csv');fig,ax=plt.subplots(1,3,figsize=(7.05,2.15),gridspec_kw={'width_ratios':[1,1,1.5],'wspace':.30});order=[('ixi','hat'),('ixi','swinir'),('fastmri','hat'),('fastmri','swinir')]
 for j,ep in enumerate(['beyond_count','fixed_count']):
  q=d[d.endpoint==ep].set_index(['dataset','model'])
  for i,key in enumerate(order):
   r=q.loc[key];ax[j].errorbar(r.estimate,3-i,xerr=[[r.estimate-r.simultaneous_low],[r.simultaneous_high-r.estimate]],fmt='o',color='#236c98',capsize=2,ms=4)
  ax[j].set_yticks(range(4),['fastMRI/SwinIR','fastMRI/HAT','IXI/SwinIR','IXI/HAT'] if j==0 else ['']*4);ax[j].axvline(0,color='.6',ls='--',lw=.6);ax[j].grid(axis='x',color='.93');ax[j].set_ylim(-.5,3.5);ax[j].tick_params(labelsize=7);ax[j].set_xlabel(r'$|\rho_I|-|\rho_{count}|$' if j==0 else 'Partial correlation',fontsize=7);ax[j].set_title('(a) Beyond count' if j==0 else '(b) Fixed count',fontsize=8,weight='bold')
 for m,col in [('hat','#236c98'),('swinir','#b86516')]:
  q=prop[prop.model==m].sort_values('epsilon');name='HAT' if m=='hat' else 'SwinIR'
  ax[2].plot(100*q.epsilon,q.observed_delta_mean,'o-',color=col,ms=3,lw=1,label=name+' observed');ax[2].plot(100*q.epsilon,q.linear_prediction_mean,'--',color=col,lw=1,label=name+' fixed local')
 ax[2].axhline(0,color='.7',lw=.5);ax[2].set_xticks([.25,.5,1,2]);ax[2].tick_params(labelsize=7);ax[2].set_xlabel('Perturbation amplitude (%)',fontsize=7);ax[2].set_ylabel(r'$\Delta\,\mathbb{E}D^2$ (native units)',fontsize=7,labelpad=1);ax[2].set_title('(c) Fixed-context validation',fontsize=8,weight='bold');ax[2].legend(fontsize=5.8,frameon=False,loc='lower left',handlelength=1.3,labelspacing=.2)
 fig.subplots_adjust(left=.16,right=.99,bottom=.22,top=.86);save(fig,'final_fig3_acquired_influence')
def cards():
 c=pd.read_csv(R/'cross_arch_shared_disjoint_intervals.csv');a=pd.read_csv(R/'acquired_only_summary.csv');s=pd.read_csv(R/'acquired_only_stability.csv');rows=[];tex=[]
 for ds in ['fastmri','ixi']:
  q=c[c.dataset==ds];o=q[q.endpoint=='observable_gap'];r=q[q.endpoint=='fixed_reference_ranking'];positive=int((r.simultaneous_low>0).sum());name='fastMRI' if ds=='fastmri' else 'IXI'
  row=dict(design='cross-architecture',cohort=ds,local_low=o.delta.min(),local_high=o.delta.max(),ranking_low=r.delta.min(),ranking_high=r.delta.max(),positive_ranking_intervals=positive,beyond_count=np.nan,fixed_count=np.nan,stability='NA',information='target-mask evaluation; acquired inputs',eligibility='local phenomenon; ranking '+str(positive)+'/20');rows.append(row)
  tex.append(f'Cross-arch. & {name} & {100*o.delta.min():.1f}--{100*o.delta.max():.1f} & {r.delta.min():.3f}--{r.delta.max():.3f} & NA & NA & NA & T & Local; rank {positive}/20 '+r'\\')
 for ds in ['fastmri','ixi']:
  for m in ['hat','swinir']:
   q=a[(a.dataset==ds)&(a.model==m)].set_index('endpoint');b=q.loc['beyond_count'];f=q.loc['fixed_count'];st=s[(s.dataset==ds)&(s.model==m)].rank_stability.min();status='PASS' if st>=.85 else 'FAIL';name='HAT' if m=='hat' else 'SwinIR';cohort='fastMRI' if ds=='fastmri' else 'IXI'
   rows.append(dict(design='acquired-only '+m,cohort=ds,local_low=np.nan,local_high=np.nan,ranking_low=np.nan,ranking_high=np.nan,positive_ranking_intervals=np.nan,beyond_count=b.estimate,fixed_count=f.estimate,stability=status,information='acquired formation; target evaluation',eligibility='scoped influence'))
   tex.append(f'Probe/{name} & {cohort} & NA & NA & {b.estimate:.3f} & {f.estimate:.3f} & {status} & A & Scoped influence '+r'\\')
 rows.append(dict(design='fixed-context covariance',cohort='ixi',local_low=np.nan,local_high=np.nan,ranking_low=np.nan,ranking_high=np.nan,positive_ranking_intervals=np.nan,beyond_count=np.nan,fixed_count=np.nan,stability='NA',information='acquired perturbations; fixed context',eligibility='local trend; no uniform bound'))
 tex.append(r'Covariance & IXI & NA & NA & NA & NA & NA & A & Local trend only \\')
 pd.DataFrame(rows).to_csv(P/'MIRA_MAIN_REPORT_CARD.csv',index=False)
 text=r'''\begin{table*}[t]\centering\scriptsize
\caption{Actual MIRA report cards. $\Delta O$ is a range across the 20 ordered pairs (pp); ranking is the range of fixed-A-error $\Delta\rho$, followed by the count of positive simultaneous intervals. Probe points and intervals are in Table~\ref{tab:neural}. T: target-derived evaluation support, acquired estimator inputs. A: acquired-only statistic/support formation, targets only for error evaluation where needed. Covariance validation measures $\Delta\mathbb E D^2$, not $\Delta O$; its unmatched fields remain NA. No values are borrowed across designs.}
\label{tab:mira-card}\setlength{\tabcolsep}{3pt}
\begin{tabular}{llrrr rlll}\toprule
Design & Cohort & Local $\Delta O$ & Ranking $\Delta\rho$ & Influence$>$count & Fixed count & Stability & Contract & Claim eligibility\\\midrule
'''+ '\n'.join(tex)+r'\bottomrule\end{tabular}\end{table*}'
 (CV/'mira_report_card_table.tex').write_text(text,encoding='utf-8')
 # Retain all detailed original report cards, independently regenerated values for new designs.
 old=pd.read_csv(P/'original_snapshot/accepted_evidence/mira_report_cards.csv')
 for i,row in old.iterrows():
  if row.design=='cross_arch_phase':
   q=c[(c.dataset==row.dataset)&(c.pair==row.pair)].set_index('endpoint')
   for ep,prefix in [('observable_gap','local'),('fixed_reference_ranking','ranking')]:
    rr=q.loc[ep];old.loc[i,'local_observable_gap' if prefix=='local' else 'ranking_gap']=rr.delta;old.loc[i,prefix+'_simultaneous_low']=rr.simultaneous_low;old.loc[i,prefix+'_simultaneous_high']=rr.simultaneous_high
  elif row.design=='acquired_influence':
   q=a[(a.dataset==row.dataset)&(a.model==row.model)].set_index('endpoint')
   for ep,field,prefix in [('beyond_count','influence_beyond_count','influence'),('fixed_count','fixed_count_association','fixed_count')]:
    rr=q.loc[ep];old.loc[i,field]=rr.estimate;old.loc[i,prefix+'_simultaneous_low']=rr.simultaneous_low;old.loc[i,prefix+'_simultaneous_high']=rr.simultaneous_high
  elif row.design=='historical_same_model_TTA':
   rr=pd.read_csv(OUT/'reproduced_architecture_headlines.csv').set_index(['dataset','model']).loc[(row.dataset,row.model)]
   for target,source in [('local_observable_gap','local_gap'),('local_simultaneous_low','local_sim_low'),('local_simultaneous_high','local_sim_high'),('ranking_gap','ranking_gap'),('ranking_simultaneous_low','ranking_sim_low'),('ranking_simultaneous_high','ranking_sim_high')]:old.loc[i,target]=rr[source]
 old.to_csv(P/'mira_report_cards.csv',index=False)
 # Regenerate Table 2 from array-derived influence and stability measurements.
 tab=[]
 for ds in ['ixi','fastmri']:
  for m in ['hat','swinir']:
   q=a[(a.dataset==ds)&(a.model==m)].set_index('endpoint');b=q.loc['beyond_count'];f=q.loc['fixed_count'];st=s[(s.dataset==ds)&(s.model==m)].rank_stability.min()
   tab.append(f"{'IXI' if ds=='ixi' else 'fastMRI'} & {'HAT' if m=='hat' else 'SwinIR'} & {b.estimate:.3f} [{b.simultaneous_low:.3f},{b.simultaneous_high:.3f}] & {f.estimate:.3f} [{f.simultaneous_low:.3f},{f.simultaneous_high:.3f}] & {st:.3f} / "+('PASS' if st>=.85 else 'FAIL')+r' \\')
 template=(P/'original_snapshot/manuscript/final_acquired_table.tex').read_text(encoding='utf-8');start=template.index('\nIXI &');end=template.index('\\bottomrule',start)
 (CV/'final_acquired_table.tex').write_text(template[:start]+'\n'+'\n'.join(tab)+'\n'+template[end:],encoding='utf-8')
def main():
 controls();influence();cards()
 source=PAPER/'FINAL_SCIENTIFIC_STRENGTHENING/scripts/final_figures.py';spec=importlib.util.spec_from_file_location('frozen_figures',source);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 mod.P=P;mod.OUT=OUT;mod.FIG=FIG
 for fn in [mod.teaser,mod.cross_arch,mod.proposition]:fn()
 for name in ['final_fig1_physical_anchors','final_fig4_cross_architecture','final_proposition_validation']:shutil.copy2(FIG/(name+'.pdf'),CV/(name+'.pdf'))
 print('All main figure inputs and report-card/table values regenerated')
if __name__=='__main__':main()
