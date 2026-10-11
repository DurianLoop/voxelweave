"""Development-only visual QC; GT selects the display slice, never the inference ROI."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='1'
import sys,json
from pathlib import Path
from datetime import datetime,timezone
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from vs_seg_task_cpu_support import resource_gate
from mc_rc_observed_only_training_input import ROOT,read,sha,read_supervised_label,reconstruct,normalize,np
# Avoid importing the neural support: loading packages is simple and authenticated.
from mc_rc_observed_only_training_input import ObservedMRI,array_sha
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_gate();out=ROOT/'figures/mc_rc_sparse_task_cpu_pilot';out.mkdir(exist_ok=False)
    rpath=ROOT/'experiments/mc_rc_sparse_task_training_cpu_pilot/attempt_01.json';r=read(rpath);cases=read(ROOT/'experiments/mc_rc_current_development_input_preparation/attempt_01.json')['cases'];rows=read(ROOT/'experiments/mc_rc_development_training_input_cpu/attempt_01.json')['series'];fig,axs=plt.subplots(1,2,figsize=(10,5),dpi=160);shown=[]
    for ax,patient in zip(axs,('VS-MC-RC-012','VS-MC-RC-013')):
        case=next(x for x in cases if x['patient']==patient);row=next(x for x in rows if x['uid']==case['uid']);e=next(x for x in r['evaluations'] if x['patient']==patient and x['method']=='raw_pchip');p=ROOT/row['observed_package'];assert sha(p)==row['observed_package_sha256']
        with np.load(p,allow_pickle=False) as q:o=ObservedMRI(q['observed_rcz'].copy(),tuple(map(int,q['observed_indices'])),int(q['native_shape'][2]),tuple(tuple(x) for x in q['affine_rcz_ras']),(),())
        raw=reconstruct(o,'raw_pchip');x,st=normalize(raw,o,'observed_shared');assert array_sha(x)==e['input_sha256'];g=read_supervised_label(case)
        with np.load(ROOT/e['prediction_file'],allow_pickle=False) as q:pred=q['prediction_rcz'].copy()
        z=int(np.argmax(g.sum(axis=(0,1))));a=x[:,:,z];lo,hi=np.percentile(a,[1,99]);ax.imshow(a,cmap='gray',vmin=lo,vmax=hi);ax.contour(g[:,:,z],levels=[.5],colors=['cyan'],linewidths=1.0)
        if pred[:,:,z].any():ax.contour(pred[:,:,z],levels=[.5],colors=['red'],linewidths=.6)
        role='training diagnostic' if patient.endswith('012') else 'held-out development';ax.set_title(patient+' | '+role+'\nfull Dice = %.5f | z = %d'%(e['metrics']['full']['dice'],z),fontsize=10);ax.axis('off');shown.append(dict(patient=patient,z=z,slice_selected_by='maximum GT foreground count, display only',display_percentiles=[float(lo),float(hi)],original_FOV=list(a.shape)))
    fig.text(.5,.02,'Sparse PCHIP only | cyan: reference VS | red: prediction | full FOV, display slice chosen after evaluation',ha='center',fontsize=8);fig.tight_layout(rect=(0,.04,1,1));image=out/'development_full_FOV_overlay.png';fig.savefig(image);plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,3.2),dpi=160);ax.plot([x['update'] for x in r['training_history']],[x['last100_loss_mean'] for x in r['training_history']]);ax.set(xlabel='Update',ylabel='Mean BCE + Dice loss (last 100)',title='10-patient sparse-task CPU pilot');ax.grid(alpha=.2);fig.tight_layout();loss=out/'training_loss.png';fig.savefig(loss);plt.close(fig)
    receipt=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),result_sha256=sha(rpath),shown=shown,full_FOV=True,GT_only_used_to_select_visual_QC_slice=True,MR_source='observed-only PCHIP, no hidden MR',publication_claim_confirmed=False,outputs=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in (image,loss)]);(out/'provenance.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt,ensure_ascii=False))
if __name__=='__main__':main()
