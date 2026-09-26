from common import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
FIG=P/'figures';FIG.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'pdf.fonttype':42,'ps.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})

def export(fig,name):
 fig.savefig(FIG/(name+'.pdf'),bbox_inches='tight',pad_inches=.03);fig.savefig(FIG/(name+'.png'),dpi=200,bbox_inches='tight',pad_inches=.03);plt.close(fig)

def teaser():
 path=PAPER/'PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/outputs/main_median_real_arrays.npz'
 with np.load(path) as f:y,a,b0,b2,m=f['gt'],f['a'],f['b_shared'],f['b_disjoint'],f['mask']
 vmax=float(np.percentile(y[m],99.5));emax=float(np.percentile(np.concatenate([abs(a-y)[m],abs(b0-y)[m],abs(b2-y)[m],abs(a-b0)[m],abs(a-b2)[m]]),99))
 fig=plt.figure(figsize=(7.05,4.15));gs=fig.add_gridspec(4,6,height_ratios=[.40,1,.40,1],left=.02,right=.995,bottom=.035,top=.89,hspace=.30,wspace=.045)
 titles=['Target GT','Prediction A','Prediction B',r'$|A-B|$',r'$|A-GT|$',r'$|B-GT|$']
 rec=[]
 for row,b in enumerate([b0,b2]):
  strip=fig.add_subplot(gs[2*row,:]);strip.set_xlim(-3.1,14.9);strip.set_ylim(-.28,1.3);strip.axis('off')
  for yy,name,anchors,col in [(.85,'A: phase 0',[0,4,8,12],'#176791'),(.15,'B: phase 0' if row==0 else 'B: phase 2',[0,4,8,12] if row==0 else [2,6,10,14],'#b86516')]:
   strip.plot([0,14],[yy,yy],color='.80',lw=.7);strip.scatter(anchors,[yy]*4,s=22,color=col,marker='s',zorder=3);strip.text(-.7,yy,name,ha='right',va='center',fontsize=7.2)
   for x in anchors:strip.text(x,yy-.18,str(x),ha='center',va='top',fontsize=6.5,color=col)
  strip.axvline(9,ymin=.05,ymax=.9,color='#ae223b',lw=1,ls=':');strip.scatter([9],[1.12],marker='v',color='#ae223b',s=22);strip.text(9.28,1.12,'same target z=9',fontsize=7,color='#ae223b',va='center')
  strip.text(14.6,1.12,'Reused anchors' if row==0 else 'Distinct anchors',ha='right',va='center',fontsize=7.2,weight='bold')
  r=metrics(a,b,y,m);rec.append(r)
  for j,im in enumerate([y,a,b,abs(a-b),abs(a-y),abs(b-y)]):
   ax=fig.add_subplot(gs[2*row+1,j]);ax.imshow(im.T,origin='lower',cmap='gray' if j<3 else 'magma',vmin=0,vmax=vmax if j<3 else emax,interpolation='nearest');ax.set_xticks([]);ax.set_yticks([])
   for sp in ax.spines.values():sp.set_visible(False)
   if row==0:ax.set_title(titles[j],fontsize=7.8,pad=2)
   if j==0:ax.set_ylabel('Shared' if row==0 else 'Disjoint',fontsize=8,labelpad=1)
   if j>=3:ax.text(.5,-.06,'MAE '+f"{r[['disagreement','reference_error','companion_error'][j-3]]:.1f}",transform=ax.transAxes,ha='center',va='top',fontsize=7)
 fig.text(.02,.985,'Identical target and reference prediction; change companion evidence',va='top',fontsize=9,weight='bold')
 fig.text(.02,.94,f'Observable error: {100*rec[0]["observable"]:.1f}% shared → {100*rec[1]["observable"]:.1f}% disjoint',fontsize=8,va='top');fig.text(.995,.94,f'All error/difference maps: 0–{emax:.0f}',fontsize=7,ha='right',va='top')
 export(fig,'final_fig1_physical_anchors');write(OUT/'figure1_annotation_manifest.json',{'source_sha256':sha(path),'target_z':9,'selection':'unchanged Plan17 median-effect example','intensity_max':vmax,'error_map_max':emax,'values':rec,'anchor_sets':[[0,4,8,12],[2,6,10,14]],'display':'identical transpose, full plane, no new crop'})

def control():
 d=pd.read_csv(OUT/'reproduced_original_control.csv').set_index('dataset').loc[['fastmri','ixi','ningxia']];fig,ax=plt.subplots(1,2,figsize=(7.05,2.25),gridspec_kw={'wspace':.35})
 y=np.arange(3)
 ax[0].errorbar(d.delta,y,xerr=np.array([d.delta-d.low,d.high-d.delta]),fmt='o',color='#23699b',capsize=3);ax[0].axvline(0,color='.5',ls='--',lw=.7);ax[0].set_yticks(y,['fastMRI','IXI','NingXia']);ax[0].invert_yaxis();ax[0].set_xlabel('Disjoint − shared pooled-plane correlation');ax[0].set_title('(a) Original clean control',weight='bold')
 o=d.observable_percent.to_numpy();ax[1].barh(y,100-o,color='#366e95',label='Common error');ax[1].barh(y,o,left=100-o,color='#cf883c',label='Observable error');ax[1].set_yticks(y,['fastMRI','IXI','NingXia']);ax[1].invert_yaxis();ax[1].set_xlim(0,110)
 for j,v in enumerate(o):ax[1].text(101,j,f'{v:.2f}%',va='center',fontsize=7)
 ax[1].set_xlabel('Paired-error energy (%)');ax[1].set_title('(b) Error under clean sharing',weight='bold');ax[1].legend(fontsize=7,loc='lower center',bbox_to_anchor=(.5,-.45),ncol=2,frameon=False)
 fig.subplots_adjust(bottom=.27,top=.84,left=.09,right=.96);export(fig,'final_fig2_original_control')

def influence():
 df=pd.read_csv(OUT/'array_reproduced/acquired_only_summary.csv');st=pd.read_csv(P/'acquired_only_stability.csv');fig,ax=plt.subplots(1,2,figsize=(7.05,2.25),gridspec_kw={'wspace':.30});order=[('ixi','hat'),('ixi','swinir'),('fastmri','hat'),('fastmri','swinir')]
 for j,ep in enumerate(['beyond_count','fixed_count']):
  q=df[df.endpoint==ep].set_index(['dataset','model'])
  for i,key in enumerate(order):
   r=q.loc[key];passed=(st[(st.dataset==key[0])&(st.model==key[1])].status=='PASS').all();col='#206ca0' if passed else '#b45c2e';ax[j].errorbar(r.estimate,3-i,xerr=[[r.estimate-r.simultaneous_low],[r.simultaneous_high-r.estimate]],fmt='o' if passed else 'x',color=col,capsize=3)
  ax[j].axvline(0,color='.5',ls='--',lw=.7);ax[j].set_yticks(range(4),[('IXI' if d=='ixi' else 'fastMRI')+' / '+('HAT' if m=='hat' else 'SwinIR') for d,m in order[::-1]] if j==0 else ['']*4);ax[j].set_ylim(-.6,3.6);ax[j].grid(axis='x',color='.92');ax[j].set_xlabel(r'$|\rho_I|-|\rho_{count}|$' if j==0 else 'Partial influence–alignment correlation');ax[j].set_title('(a) Acquired-only non-self grid' if j==0 else '(b) Exactly one shared anchor',fontsize=8,weight='bold')
 fig.subplots_adjust(left=.19,right=.99,bottom=.22,top=.85);export(fig,'final_fig3_acquired_influence')

def cross_arch():
 df=pd.read_csv(OUT/'array_reproduced/cross_arch_shared_disjoint_intervals.csv');df[['a','b']]=df.pair.str.split('__',expand=True);fig,ax=plt.subplots(1,2,figsize=(7.05,3.25));local=df[df.endpoint=='observable_gap'];limit=max(.05,float(abs(local.delta).max()));norm=TwoSlopeNorm(vmin=-limit,vcenter=0,vmax=limit)
 names=['HAT','SwinIR','I3Net','SAINT','CycleINR']
 for j,ds in enumerate(['fastmri','ixi']):
  g=local[local.dataset==ds].set_index(['a','b']);mat=np.full((5,5),np.nan)
  for i,a in enumerate(MODELS):
   for k,b in enumerate(MODELS):
    if a==b:continue
    r=g.loc[(a,b)];mat[i,k]=r.delta
  im=ax[j].imshow(mat,cmap='RdBu',norm=norm)
  for i,a in enumerate(MODELS):
   for k,b in enumerate(MODELS):
    if a==b:ax[j].text(k,i,'—',ha='center',va='center',color='.5');continue
    r=g.loc[(a,b)];star='*' if r.simultaneous_low>0 or r.simultaneous_high<0 else '';ax[j].text(k,i,f'{100*r.delta:.1f}{star}',ha='center',va='center',fontsize=8,color='white' if abs(r.delta)>.65*limit else '#15202c')
  ax[j].set_xticks(range(5),names,rotation=35,ha='right');ax[j].set_yticks(range(5),names);ax[j].set_xlabel('Companion B: phase 0 → phase 2');ax[j].set_ylabel('Fixed reference A: phase 0');ax[j].set_title(('(a) fastMRI, 24 examinations' if j==0 else '(b) IXI, 115 examinations'),fontsize=8,weight='bold')
 fig.subplots_adjust(left=.10,right=.92,bottom=.24,top=.90,wspace=.45);bar=fig.add_axes([.945,.28,.018,.58]);fig.colorbar(im,cax=bar).set_label('Observable fraction gain',fontsize=7);fig.text(.10,.015,'Cells: percentage-point gain; * simultaneous 95% interval excludes zero (20 ordered pairs/cohort).',fontsize=7);export(fig,'final_fig4_cross_architecture')

def proposition():
 d=pd.read_csv(OUT/'array_reproduced/proposition_summary.csv');raw=pd.read_csv(OUT/'array_reproduced/proposition1_neural_validation.csv');fig,ax=plt.subplots(1,2,figsize=(7.05,2.6),gridspec_kw={'wspace':.32});colors={'hat':'#236f9a','swinir':'#b66822'}
 for model in ['hat','swinir']:
  g=d[d.model==model].sort_values('epsilon');col=colors[model]
  ax[0].plot(100*g.epsilon,-g.observed_delta_mean,'o-',color=col,label=model.upper()+' observed',ms=4)
  ax[0].plot(100*g.epsilon,-g.linear_prediction_mean,'--',color=col,label=model.upper()+' fixed linear')
  for j,eps in enumerate([.0025,.005,.01,.02]):
   q=raw[(raw.model==model)&(raw.epsilon==eps)];x=j+(-.12 if model=='hat' else .12);ax[1].scatter(np.full(len(q),x),100*q.approx_relative_error,color=col,s=9,alpha=.35,edgecolors='none')
   ax[1].plot([x-.07,x+.07],[100*q.approx_relative_error.median()]*2,color=col,lw=2)
 ax[0].set_xlabel('Perturbation amplitude (%)');ax[0].set_ylabel('Disagreement-energy suppression');ax[0].set_title('(a) One fixed local prediction',fontsize=8,weight='bold');ax[0].legend(fontsize=6,frameon=False)
 ax[1].set_xticks(range(4),['0.25','0.5','1','2']);ax[1].set_xlabel('Perturbation amplitude (%)');ax[1].set_ylabel('Individual approximation error (%)');ax[1].set_title('(b) Every case/context retained',fontsize=8,weight='bold');ax[1].axhline(0,color='.7',lw=.7)
 fig.subplots_adjust(left=.09,right=.99,bottom=.22,top=.87);export(fig,'final_proposition_validation')

if __name__=='__main__':
 from regenerate_tables import main as regenerate_tables
 regenerate_tables()
 teaser()
 if (OUT/'reproduced_original_control.csv').exists():control()
 if (OUT/'acquired_only_summary.csv').exists():influence()
 if (P/'cross_arch_shared_disjoint_intervals.csv').exists():cross_arch()
 if (OUT/'array_reproduced/proposition_summary.csv').exists():proposition()
