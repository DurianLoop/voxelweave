from common import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
import shutil
FIG=P/'figures';FIG.mkdir(exist_ok=True);CV=PAPER/'CVPR/CVPR_ARCH_GENERALIZED/PAPER'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'ps.fonttype':42})
def export(fig,name):
 fig.savefig(FIG/(name+'.pdf'),bbox_inches='tight',pad_inches=.025);fig.savefig(FIG/(name+'.png'),dpi=220,bbox_inches='tight',pad_inches=.025)
 shutil.copy2(FIG/(name+'.pdf'),CV/'figures'/(name+'.pdf'));plt.close(fig)
def flow(ax,items,colors):
 ax.set_xlim(0,1);ax.set_ylim(0,1);ax.axis('off');n=len(items);w=.91/n
 for i,(s,color) in enumerate(zip(items,colors)):
  x=i/n+.007;ax.add_patch(FancyBboxPatch((x,.14),w,.72,boxstyle='round,pad=.008,rounding_size=.025',fc=color,ec='#536372',lw=.65))
  ax.text(x+w/2,.5,s,ha='center',va='center',fontsize=7)
  if i<n-1:ax.annotate('',xy=((i+1)/n,.5),xytext=(x+w+.003,.5),arrowprops={'arrowstyle':'->','lw':.8,'color':'#344451'})
def qualitative(role,name):
 ar=np.load(OUT/(role+'_real_arrays.npz'));y=ar['gt'];a=ar['a'];bs=[ar['b_shared'],ar['b_disjoint']];mask=ar['mask']
 rec=next(r for r in json.loads((OUT/'qualitative_inference.json').read_text())['records'] if r['selection']['role']==role)
 vmax=float(np.percentile(y[mask],99.5));emax=float(np.percentile(np.concatenate([abs(a-y)[mask]]+[abs(b-y)[mask] for b in bs]+[abs(a-b)[mask] for b in bs]),99))
 fig=plt.figure(figsize=(7.05,3.5));gs=fig.add_gridspec(3,6,height_ratios=[1,1,.38],left=.025,right=.98,bottom=.025,top=.89,wspace=.04,hspace=.19)
 titles=['Target GT','Prediction A','Prediction B',r'$|A-B|$',r'$|A-GT|$',r'$|B-GT|$']
 for row,b in enumerate(bs):
  panels=[y,a,b,abs(a-b),abs(a-y),abs(b-y)]
  for col,im in enumerate(panels):
   ax=fig.add_subplot(gs[row,col]);ax.imshow(im.T,cmap='gray' if col<3 else 'magma',vmin=0,vmax=vmax if col<3 else emax,origin='lower',interpolation='nearest');ax.set_xticks([]);ax.set_yticks([])
   for spine in ax.spines.values():spine.set_visible(False)
   if row==0:ax.set_title(titles[col],fontsize=8,pad=3)
   if col==0:ax.set_ylabel('Shared' if row==0 else 'Disjoint',fontsize=8,labelpad=1)
   if col in (3,4,5):
    key='shared' if row==0 else 'disjoint';v=rec[key]['disagreement' if col==3 else 'mae_a' if col==4 else 'mae_b'];ax.text(.5,-.055,f'MAE {v:.1f}',transform=ax.transAxes,ha='center',va='top',fontsize=7)
 ax=fig.add_subplot(gs[2,:]);flow(ax,['Shared physical\nmeasurements','Aligned local\nresponses','Aligned target errors\n'+r'$\langle e_A,e_B\rangle>0$','Common error hidden\nin disagreement'],['#eef3f8','#eef3f8','#fff1e0','#fff1e0'])
 fig.text(.025,.985,'Same target, same frozen SwinIR estimator',fontsize=9,weight='bold',va='top')
 fig.text(.025,.938,f'Observable error: {100*rec["shared"]["observable"]:.1f}% shared  →  {100*rec["disjoint"]["observable"]:.1f}% disjoint',fontsize=8,va='top')
 fig.text(.98,.937,f'All difference/error maps: 0–{emax:.0f}',fontsize=7,ha='right',va='top')
 export(fig,name)
 return {'role':role,'intensity_vmax':vmax,'all_difference_error_vmax':emax,'selection':rec['selection'],'no_manual_crop':True,'display_transpose':'same transpose applied to every panel, no clinical orientation label inferred'}
def framework():
 fig,ax=plt.subplots(figsize=(7.0,2.35));ax.axis('off');ax.set_xlim(0,1);ax.set_ylim(0,1)
 boxes=[(.00,.60,.26,.34,'INPUT CONTRACT\nFrozen F; target location z\nAnchor IDs and contexts\nSupport and preprocessing','#edf2f8'),(.36,.60,.27,.34,'SAME-TARGET PAIRS\nVary anchor identity\nRecord geometry differences\nPredictions A, B; difference D','#edf2f8'),(.73,.60,.265,.34,'AUDIT OUTPUT\nHidden common error\nInfluence stability\nRanking scope and failures','#e9f4f0'),(.00,.03,.39,.40,'LOCAL INFLUENCE\nEmbedded linear coefficients, or\nmatched neural anchor perturbations\nUse ALL-anchor response energy\nCheck amplitude/sign stability','#fff3e5'),(.53,.03,.465,.40,'RETROSPECTIVE EVALUATION\nGT: alignment and error-energy fractions\nResample examinations / patients\nRetain failed models and NA endpoints\nDisclose historical GT masks / scales','#f3f3f3')]
 for x,y,w,h,s,color in boxes:
  ax.add_patch(FancyBboxPatch((x+.005,y),w-.01,h,boxstyle='round,pad=.008,rounding_size=.018',fc=color,ec='#536372',lw=.8));ax.text(x+w/2,y+h/2,s,ha='center',va='center',fontsize=7.2,linespacing=1.4)
 for start,end in [((.27,.77),(.35,.77)),((.49,.59),(.49,.48)),((.49,.48),(.20,.48)),((.20,.48),(.20,.44)),((.40,.23),(.52,.23)),((.86,.44),(.86,.59))]:
  ax.annotate('',xy=end,xytext=start,arrowprops={'arrowstyle':'->','lw':.8,'color':'#344451'})
 export(fig,'p17_framework')
def influence():
 up=PAPER/'CVPR/archive/CVPR_UPGRADE/outputs'
 a=pd.read_csv(OUT/'nonself_influence_summary.csv').rename(columns={'advantage':'abs_rho_advantage','simultaneous_low':'advantage_ci_low','simultaneous_high':'advantage_ci_high'})
 b=pd.read_csv(up/'plan6_fixed_overlap_ladder.csv').query("endpoint=='error_cosine'")
 q=a.merge(b,on=['dataset','model'],suffixes=('','_fixed'))
 order=[(d,m) for d in ['fastmri','ixi','ningxia'] for m in ['hat','swinir']];q=q.set_index(['dataset','model']).loc[order].reset_index();q.to_csv(OUT/'figure_influence_data.csv',index=False)
 fig,axs=plt.subplots(1,2,figsize=(7.05,2.45),gridspec_kw={'wspace':.28});labels=[d+' / '+m.upper() for d,m in order]
 for j,(point,lo,hi,title) in enumerate([('abs_rho_advantage','advantage_ci_low','advantage_ci_high','(a) Non-self grid: influence minus count'),('partial_rho_neural_influence','cluster_ci_low','cluster_ci_high','(b) Exactly one shared anchor')]):
  ax=axs[j]
  for i,r in q.iterrows():
   color='#226aa7' if r.dataset!='ningxia' else '#bd641c';ax.errorbar(r[point],5-i,xerr=[[r[point]-r[lo]],[r[hi]-r[point]]],fmt='o',ms=4,color=color,capsize=3,lw=1)
  ax.axvline(0,color='.4',lw=.8,ls='--');ax.set_yticks(range(6),labels[::-1] if j==0 else ['']*6);ax.set_ylim(-.65,5.65);ax.set_title(title,fontsize=8,weight='bold');ax.grid(axis='x',color='.92')
  ax.set_xlabel(r'$|\rho_I|-|\rho_{count}|$' if j==0 else 'Adjusted influence–alignment correlation',fontsize=8)
 fig.subplots_adjust(left=.19,right=.99,bottom=.20,top=.88);export(fig,'p17_influence_beyond_count')
if __name__=='__main__':
 records=[qualitative('main_median','p17_qualitative_teaser'),qualitative('supplement_seeded_random','p17_qualitative_random')];framework();influence();save('figure_manifest.json',{'qualitative':records,'scientific_data_not_image_generated':True})
 print('Four scientific figures generated from arrays/CSV/vector primitives.')
