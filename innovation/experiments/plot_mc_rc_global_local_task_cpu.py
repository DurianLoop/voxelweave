"""Plot all patients and complete training history; no model inference or label selection."""
import os
for name in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[name]='1'
import json,hashlib
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from vs_seg_task_cpu_support import resource_gate
ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    resource_gate()
    trainfile=ROOT/'experiments/mc_rc_global_local_task_training_cpu/attempt_01.json'
    valfile=ROOT/'experiments/mc_rc_global_local_task_validation_cpu/attempt_01.json'
    proofile=valfile.parent/'independent_metrics_and_checkpoint_attempt_01.json'
    train,val,proof=[read(p) for p in (trainfile,valfile,proofile)]
    assert all(r['complete'] and not r['errors'] for r in (train,val,proof))
    assert proof['result_sha256']==sha(valfile)
    out=ROOT/'figures/mc_rc_global_local_task_cpu';out.mkdir(exist_ok=False)
    fig,axs=plt.subplots(1,3,figsize=(14,4.6),layout='constrained')
    h=train['training_history'];steps=[r['update'] for r in h]
    for index,label in enumerate(('Total','Local','Global')):
        axs[0].plot(steps,[r['last100_loss_mean'][index] for r in h],label=label,linewidth=1.5)
    axs[0].set(xlabel='Training updates',ylabel='BCE + soft Dice loss',title='Fixed training budget')
    axs[0].legend(frameon=False)
    patients=sorted(val['aggregate']['raw_pchip']['patients'])
    x=np.arange(len(patients))
    for ax,domain,gate in zip(axs[1:],('full','missing'),(.70,.65)):
        for offset,method,color in ((-.18,'raw_pchip','#2467a4'),(.18,'raw_linear','#d67d32')):
            values=[val['aggregate'][method]['patients'][p]['metrics'][domain]['dice'] for p in patients]
            assert all(v is not None for v in values)
            ax.bar(x+offset,values,width=.34,color=color,label=method.replace('raw_',''))
        ax.set_xticks(x,[p[-3:] for p in patients])
        ax.set(ylim=(0,1),xlabel='Fixed validation patient',ylabel='Within-patient mean Dice',
               title='Full native grid' if domain=='full' else 'Supported missing planes')
        ax.axhline(gate,color='#555555',linestyle='--',linewidth=1,label='Mean capability target')
        ax.legend(frameon=False,fontsize=9)
    for ax in axs:
        ax.spines[['right','top']].set_visible(False)
    fig.suptitle('Capability baseline only; four patients, nine series; no scientific confirmation',fontsize=12)
    image=out/'training_and_all4_validation_patients.png'
    fig.savefig(image,dpi=160);plt.close(fig)
    provenance=dict(script_sha256=sha(__file__),
        outputs=[dict(path=image.relative_to(ROOT).as_posix(),sha256=sha(image))],
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p))
                         for p in (trainfile,valfile,proofile)],neural_forward_calls=0,
        all_validation_patients_shown=True,scientific_confirmation_patients=0)
    (out/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(provenance['outputs']))
if __name__=='__main__':main()
