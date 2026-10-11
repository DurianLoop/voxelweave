"""Standalone scientific figure for the completed analytic diagnostic only."""
import json,os,sys
from pathlib import Path
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[key]='1'
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from vs_seg_task_cpu_support import ROOT,resource_gate
from vs_seg_full_volume_runtime import sha
OUT=ROOT/'experiments/vs_seg_resampling_order_cpu'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def main():
 sys.stdout.reconfigure(encoding='utf-8');resource_gate();d=read(OUT/'attempt_01.json');proof=read(OUT/'independent_replay_attempt_01.json')
 if not d['complete'] or not proof['complete'] or proof['errors'] or proof['result_sha256']!=sha(OUT/'attempt_01.json'): raise ValueError('Complete all45 analytic proof required')
 patients=[read(ROOT/r['file']) for r in d['patients']];fig,axes=plt.subplots(1,2,figsize=(12,4.6),gridspec_kw={'width_ratios':[1,1.2]});fig.patch.set_facecolor('white');colors={'linear':'#48789b','pchip':'#a24838'}
 for kernel in ('linear','pchip'):
  axes[0].plot(np.arange(1,46),[p['kernels'][kernel]['order']['max_abs_normalized_difference_full_image'] for p in patients],marker='o',markersize=3,lw=1.1,label=kernel.upper(),color=colors[kernel])
 axes[0].axhline(1e-6,color='#777777',ls='--',lw=1,label='Prespecified numerical tolerance');axes[0].set_yscale('log');axes[0].set(xlabel='Patient in frozen roster (45 CISS)',ylabel='Max pixel difference / observed intensity range',title='A. Pipeline vs post-resize output');axes[0].legend(loc='center left',fontsize=8,frameon=False);axes[0].grid(axis='y',alpha=.17)
 names=['Support','JSON lesion','RT lesion'];regions=['support','original_json_lesion','rtstruct_lesion'];comp=['pipeline-post_resize','pipeline-raw'];c={'pipeline-post_resize':'#a24838','pipeline-raw':'#48789b'}
 for j,comparison in enumerate(comp):
  entries=[next(e for e in d['analysis'] if e['kernel']=='pchip' and e['region']==r and e['weighting']=='target_equal_nmse' and e['comparison']==comparison)['estimate'] for r in regions];mean=np.array([e['mean_difference'] for e in entries])*1e4;ci=np.array([e['ci95_percentile'] for e in entries])*1e4;positions=np.arange(3)+(j-.5)*.19
  axes[1].errorbar(mean,positions,xerr=np.stack((mean-ci[:,0],ci[:,1]-mean)),fmt='o',capsize=3,color=c[comparison],label='Pipeline - post (order)' if j==0 else 'Pipeline - raw (whole path)',markersize=4)
 axes[1].axvline(0,color='#777777',lw=1);axes[1].set_yticks(np.arange(3),names);axes[1].invert_yaxis();axes[1].set(xlabel='Mean NMSE difference (x 10^-4)\nNegative = lower error',title='B. PCHIP image-error changes');axes[1].legend(loc='upper left',fontsize=8,frameon=False);axes[1].grid(axis='x',alpha=.17)
 for ax in axes:
  ax.spines[['top','right']].set_visible(False)
 fig.text(.01,.012,'45 already-seen patients; 2,565 missing slices. Patient/target equal weighting. Descriptive 95% bootstrap intervals; no new Dice or clinical claim.',fontsize=8,color='#444444');fig.tight_layout(rect=(0,.065,1,1));outputs=[]
 for suffix in ('png','svg'):
  p=OUT/('resampling_order_image_diagnostic_attempt_02.'+suffix)
  if p.exists(): raise FileExistsError('Retain earlier figure')
  fig.savefig(p,dpi=170,facecolor='white');outputs.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),bytes=p.stat().st_size))
 plt.close(fig);p=OUT/'figure_provenance_attempt_02.json';p.write_text(json.dumps(dict(script_sha256=sha(__file__),result_sha256=sha(OUT/'attempt_01.json'),proof_sha256=sha(OUT/'independent_replay_attempt_01.json'),outputs=outputs,task_results_included=False,visual_review_completed=False,earlier_attempt_retained='figure_provenance.json; first figure legend overlapped RT interval and was corrected'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(outputs=outputs,task_results_included=False)))
if __name__=='__main__': main()
