"""Scientific PNG/SVG from completed all45 proofs; no interactive windows."""
import os
os.environ['MPLBACKEND']='Agg'
os.environ['OMP_NUM_THREADS']='1'
import csv,json,math,sys
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
import matplotlib.pyplot as plt
from vs_seg_full_volume_runtime import sha
from vs_seg_task_cpu_support import ROOT,resource_gate
OUT=ROOT/'experiments/vs_seg_post_resize_task_cpu'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def main():
 sys.stdout.reconfigure(encoding='utf-8');resource_gate();r=read(OUT/'attempt_01.json');p=read(OUT/'independent_all_tasks_and_estimates.json');band=ROOT/'experiments/anchor_bandwidth_diagnostic_cpu';b=read(band/'attempt_01.json');q=read(band/'independent_gradient_and_identities.json');assert all(x['complete'] and not x['errors'] for x in (r,p,b,q));assert p['result_sha256']==sha(OUT/'attempt_01.json') and q['result_sha256']==sha(band/'attempt_01.json');csvpath=OUT/'all45_task_dice.csv'
 with csvpath.open(encoding='utf-8-sig',newline='') as stream:rows=list(csv.DictReader(stream))
 assert len(rows)==45;fig,axes=plt.subplots(1,3,figsize=(13.5,4.5));fig.subplots_adjust(left=.06,right=.98,top=.83,bottom=.28,wspace=.34);colors=['#1f77b4','#b45a36','#6554a3']
 for ax,ref,title in zip(axes[:2],('original_json','rtstruct'),('Original JSON reference','RTSTRUCT reference')):
  y=np.array([[float(row[f'{ref}_full_{name}']) for name in ('raw','pipeline','post')] for row in rows]);x=np.arange(3)
  for line in y:ax.plot(x,line,color='#b3b8c0',alpha=.38,lw=.6,zorder=1)
  means=y.mean(axis=0);ax.plot(x,means,color='#263747',lw=2,zorder=3)
  for i,value in enumerate(means):ax.scatter(i,value,c=colors[i],s=45,zorder=4);ax.text(i,value+.045,f'{value:.4f}',ha='left' if i==0 else 'center',fontsize=10,fontweight='bold')
  ax.set_xticks(x,['Raw PCHIP','Pipeline','Post resize'],fontsize=10);ax.set_ylim(-.025,1.04);ax.set_ylabel('Full-volume Dice',fontsize=10);ax.set_title(title,fontsize=11);ax.grid(axis='y',alpha=.17);ax.spines[['top','right']].set_visible(False)
 records=[read(ROOT/e['file']) for e in b['patients']];ax=axes[2];names=['raw','mixed_post','raw_anchor_roundtrip','slab_roundtrip'];labels=['Raw PCHIP','Missing layers resized','Anchors resized only','Anchors + missing resized'];linecolors=['#1f77b4','#b45a36','#8f697b','#27846f'];styles=['-','--',':','-.']
 for name,label,color,style in zip(names,labels,linecolors,styles):
  values=np.array([[e/r['summaries']['raw']['phase_mean_energy'][0] for e in r['summaries'][name]['phase_mean_energy']] for r in records]);ax.plot(np.arange(4),values.mean(axis=0),marker='o',lw=1.8,color=color,ls=style,label=label)
 ax.set_xticks(range(4),['0\nanchor','1\ninserted','2\ninserted','3\ninserted']);ax.set_ylim(0,1.1);ax.set_ylabel('In-plane gradient energy / raw anchor energy',fontsize=9);ax.set_title('Four-slice phase diagnostic',fontsize=11);ax.grid(axis='y',alpha=.17);ax.spines[['top','right']].set_visible(False);ax.legend(loc='upper center',bbox_to_anchor=(.5,-.21),fontsize=8,frameon=False,ncol=2,columnspacing=.9)
 fig.suptitle('45 seen CISS patients: task response and processing-induced phase differences',fontsize=13,fontweight='bold',y=.97);fig.text(.06,.055,'Lines in the Dice panels show all 45 patients; bold markers show means. Phase curves average patient-normalized energies.\nControls that resize observed anchors are explanatory interventions. No independent scientific cohort or new SR claim.',fontsize=9,color='#46515c');outputs=[]
 for ext in ('png','svg'):
  path=OUT/('post_task_and_bandwidth_diagnostic_attempt_02.'+ext);fig.savefig(path,dpi=180);outputs.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path)))
 plt.close(fig);prov=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),task_result_sha256=sha(OUT/'attempt_01.json'),task_proof_sha256=sha(OUT/'independent_all_tasks_and_estimates.json'),bandwidth_result_sha256=sha(band/'attempt_01.json'),bandwidth_proof_sha256=sha(band/'independent_gradient_and_identities.json'),task_csv_sha256=sha(csvpath),outputs=outputs,visual_review_completed=False,publication_claim_confirmed=False);(OUT/'figure_provenance_attempt_02.json').write_text(json.dumps(prov,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(prov,ensure_ascii=False))
if __name__=='__main__':main()
