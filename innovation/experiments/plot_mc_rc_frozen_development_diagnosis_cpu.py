"""Standalone scientific plot of all independently checked developer patient metrics."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import json,hashlib,sys
from pathlib import Path
from vs_seg_task_cpu_support import resource_gate
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_gate()
    folder=ROOT/'experiments/mc_rc_frozen_global_local_development_diagnosis_cpu_attempt02'
    rp=folder/'attempt_01.json';qp=folder/'independent_metrics_and_checkpoint_attempt_01.json'
    r,q=[json.loads(p.read_text(encoding='utf-8')) for p in (rp,qp)]
    assert r['complete'] and q['complete'] and not r['errors'] and not q['errors'] and q['result_sha256']==sha(rp)
    out=ROOT/'figures/mc_rc_frozen_development_diagnosis_cpu';out.mkdir(exist_ok=False)
    rows=r['aggregate']['patients'];patients=list(rows);x=np.arange(len(patients))
    fig,axes=plt.subplots(1,2,figsize=(12.5,4.4),layout='constrained')
    axes[0].bar(x-.18,[rows[p]['metrics']['full']['dice'] for p in patients],.36,label='Full volume',color='#315B84')
    axes[0].bar(x+.18,[rows[p]['metrics']['missing']['dice'] for p in patients],.36,label='Supported missing planes',color='#C07939')
    axes[0].set(ylabel='Dice',ylim=(0,.5),title='Spatial overlap')
    axes[0].legend(frameon=False,fontsize=9)
    values=[rows[p]['metrics']['full']['absolute_relative_volume_error'] for p in patients]
    axes[1].bar(x,values,.64,color='#567D69');axes[1].set_yscale('log')
    axes[1].set(ylabel='Absolute relative volume error (ratio)',ylim=(.45,100),title='Volume error')
    for j,v in enumerate(values):axes[1].text(j,v*1.13,f'{v:.2f}',ha='center',va='bottom',fontsize=8)
    for ax in axes:
        ax.set_xticks(x,[p[-3:] for p in patients]);ax.set_xlabel('Developer patient (series averaged within patient)')
        ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.17);ax.set_axisbelow(True)
    fig.suptitle('Frozen 20k model: training-set full-FOV diagnosis (11 patients / 19 series)',fontsize=12)
    outputs=[]
    for extension in ('png','svg'):
        p=out/('all11_developer_patients.'+extension);fig.savefig(p,dpi=180)
        outputs.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)))
    plt.close(fig)
    (out/'provenance.json').write_text(json.dumps(dict(script_sha256=sha(__file__),
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in (rp,qp)],outputs=outputs,
        patient_count=11,series_count=19,volume_error_axis_logarithmic=True,
        scientific_confirmation_patients=0,publication_claim_confirmed=False),indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(outputs=outputs)))
if __name__=='__main__':main()
