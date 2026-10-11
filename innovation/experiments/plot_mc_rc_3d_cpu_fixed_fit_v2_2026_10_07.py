"""Separate bounded overlap metrics from unbounded absRVE; keep original plot intact."""
import hashlib,json,os,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
FIG=ROOT/'figures/mc_rc_3d_cpu_fixed_fit_2026_10_07'
FIT=ROOT/'experiments/mc_rc_3d_cpu_fixed_fit_2026_10_07'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    result=FIT/'attempt_01.json';proof=FIT/'independent_both512_and_full_fov_2026_10_07.json'
    diagpath=ROOT/'experiments/mc_rc_3d_final_patch_diagnostic_2026_10_07/attempt01.json'
    p=json.loads(result.read_text(encoding='utf-8'));q=json.loads(proof.read_text(encoding='utf-8'))
    d=json.loads(diagpath.read_text(encoding='utf-8'))
    assert all(x['complete'] and not x['errors'] for x in (p,q,d))
    assert q['result_sha256']==d['fit_result_sha256']==sha(result)
    dest=FIG/'provenance_v2.json';assert not dest.exists()
    os.environ['MPLCONFIGDIR']=str(FIG/'mplconfig_v2')
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    fig,axes=plt.subplots(1,4,figsize=(16,4.7),layout='constrained')
    labels=['Native reference','Raw PCHIP'];colors=['#176c9c','#b46623']
    for i,a in enumerate(p['arms']):
        axes[0].plot([h['update'] for h in a['every_update_history']],
                     [h['loss'] for h in a['every_update_history']],color=colors[i],label=labels[i])
    axes[0].set(xlabel='Update',ylabel='Deep-supervision BCE + Dice loss',title='Fixed batch; last checkpoint')
    axes[0].legend(frameon=False,fontsize=9)
    for i,a in enumerate(p['arms']):
        vals=[a['patch_metrics'][0]['dice'],a['metrics']['full']['dice'],a['metrics']['full']['recall']]
        bars=axes[1].bar(np.arange(3)+(i-.5)*.3,vals,width=.28,color=colors[i])
        for bar,v in zip(bars,vals):axes[1].text(bar.get_x()+bar.get_width()/2,v+.02,f'{v:.3f}',ha='center',fontsize=8)
    axes[1].axhline(.9,color='#444444',linestyle='--',linewidth=1)
    axes[1].set(ylim=(0,1.09),ylabel='Metric (dashed: fixed 0.9 gate)',title='Crop and full FOV overlap')
    axes[1].set_xticks(np.arange(3),['Training crop Dice','Full FOV Dice','Full FOV recall'],rotation=35,ha='right')
    vals=[a['metrics']['full']['absRVE'] for a in p['arms']]
    bars=axes[2].bar(np.arange(2),vals,color=colors,width=.58)
    for bar,v in zip(bars,vals):axes[2].text(bar.get_x()+bar.get_width()/2,v+.10,f'{v:.3f}',ha='center')
    axes[2].axhline(.25,color='#444444',linestyle='--',linewidth=1)
    axes[2].set(ylim=(0,max(vals)*1.16),ylabel='Absolute relative volume error',title='Full FOV volume gate')
    axes[2].set_xticks(np.arange(2),labels,rotation=35,ha='right')
    axes[2].text(.02,.07,'Fixed gate: <= 0.25',transform=axes[2].transAxes,fontsize=9)
    for i,a in enumerate(d['arms']):
        axes[3].plot(np.arange(4),[v['heads'][0]['hard_metrics'][0]['dice'] for v in a['variants']],
                     color=colors[i],marker='o')
    axes[3].set(ylim=(0,1.03),ylabel='Foreground crop hard-Dice',title='Four frozen crop variants')
    axes[3].set_xticks(np.arange(4),['Training aug.','Flips only','Intensity only','Identity'],rotation=35,ha='right')
    fig.suptitle('One development series; two CPU fits; 512 updates each',fontsize=14)
    fig.supxlabel('Both original fit gates failed. Training diagnostics; no held-out task qualification.',fontsize=10)
    files=[]
    for ext in ('png','svg'):
        path=FIG/('fixed_fit_results_v2.'+ext);assert not path.exists();fig.savefig(path,dpi=170)
        files.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path)))
    plt.close(fig)
    record=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
                script_sha256=sha(Path(__file__)),result_sha256=sha(result),replay_sha256=sha(proof),
                diagnostic_sha256=sha(diagpath),figures=files,original_plot_preserved=True,
                visual_review_completed=False,scientific_confirmation_patients=0)
    with dest.open('x',encoding='utf-8') as f:json.dump(record,f,indent=2);f.write('\n')
    print(json.dumps(dict(complete=True,figures=[v['path'] for v in files])))
if __name__=='__main__':main()
