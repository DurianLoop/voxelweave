"""Standalone scientific figure of existing supervision counts; no MR or model inference."""
import hashlib,json,os,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'figures/mc_rc_3d_supervision_density_2026_10_07'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    os.environ['MPLCONFIGDIR']=str(OUT/'mplconfig')
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    source=ROOT/'experiments/mc_rc_3d_development_supervision_2026_10_07/attempt_01.json'
    digest=ROOT/'experiments/mc_rc_3d_supervision_density_2026_10_07/attempt01.json'
    data=json.loads(source.read_text(encoding='utf-8'));summary=json.loads(digest.read_text(encoding='utf-8'))
    assert data['complete'] and summary['complete'] and summary['source_sha256']==sha(source)
    fig,axes=plt.subplots(1,3,figsize=(13,4.7),gridspec_kw={'width_ratios':[1.8,1,1]},layout='constrained')
    labels=[];seen={};totals={}
    for s in data['series']:totals[s['patient']]=totals.get(s['patient'],0)+1
    for s in data['series']:
        p=s['patient'];seen[p]=seen.get(p,0)+1
        labels.append(p.rsplit('-',1)[-1]+(chr(96+seen[p]) if totals[p]>1 else ''))
    force=np.array([s['forced_fine_fraction']['median']*100 for s in summary['series']])
    batch=np.array([s['batch_fine_fraction']['median']*100 for s in summary['series']])
    x=np.arange(len(force));axes[0].scatter(x,force,label='Forced foreground crop',color='#176c9c',s=24)
    axes[0].scatter(x,batch,label='Whole batch',color='#b46623',marker='s',s=22)
    axes[0].set_yscale('log');axes[0].set_xticks(x,labels,rotation=70);axes[0].set_ylabel('Median foreground voxels (%)')
    axes[0].set_xlabel('Development series (patient number + series suffix)');axes[0].set_title('Foreground density varies by series')
    axes[0].legend(frameon=False,fontsize=8);axes[0].grid(axis='y',alpha=.2)
    errors=[[],[]];positives=0
    for s in data['series']:
        for draw in s['draws']:
            c=draw['patch_foreground_by_scale'];positives+=int(c[0][1]>0)
            for k,factor in enumerate((2,4),start=1):
                for sample in (0,1):
                    if c[0][sample]>0:errors[k-1].append(c[k][sample]*factor**3/c[0][sample]-1)
    assert positives==167 and [len(v) for v in errors]==[775,775]
    axes[1].boxplot(errors,tick_labels=['Half grid','Quarter grid'],showfliers=True,
                    flierprops={'markersize':2,'alpha':.4},medianprops={'color':'#176c9c'})
    axes[1].axhline(0,color='#666666',linewidth=.8);axes[1].set_ylabel('Coarse / fine foreground volume - 1')
    axes[1].set_title('Nearest label volume differs')
    axes[1].text(.5,.015,'775 ratios per scale; 441 empty crops undefined',transform=axes[1].transAxes,
                 ha='center',va='bottom',fontsize=7)
    zeros=summary['uniform_fine_positive_coarse_zero'];axes[2].bar(['Half grid','Quarter grid'],zeros,color=['#176c9c','#b46623'],width=.55)
    for i,n in enumerate(zeros):axes[2].text(i,n+.4,f'{n} / {positives}',ha='center',fontsize=10)
    axes[2].set_ylim(0,21);axes[2].set_ylabel('Uniform crops losing all coarse foreground')
    axes[2].set_title('Fine-positive uniform crops')
    axes[2].text(.5,.015,'Forced foreground crop: 0 at both scales',transform=axes[2].transAxes,
                 ha='center',va='bottom',fontsize=7)
    fig.suptitle('Development label diagnostics: 19 series, 32 repeated draws per series',fontsize=13)
    fig.supxlabel('Descriptive crop diagnostics; no model outcome, causal claim or independent-patient significance',fontsize=9)
    files=[]
    for ext in ('png','svg'):
        path=OUT/('supervision_density.'+ext);fig.savefig(path,dpi=180);files.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path)))
    plt.close(fig)
    record=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,source_sha256=sha(source),
                summary_sha256=sha(digest),script_sha256=sha(Path(__file__)),figures=files,
                series_tick_mapping=[dict(label=l,patient=s['patient'],uid=s['uid']) for l,s in zip(labels,data['series'])],
                actual_training_updates=0,neural_forwards=0,visual_review_completed=False,
                ratio_undefined_empty_crops_retained=441)
    with (OUT/'provenance.json').open('x',encoding='utf-8') as f:json.dump(record,f,indent=2);f.write('\n')
    print(json.dumps(dict(complete=True,files=[v['path'] for v in files])))
if __name__=='__main__':main()
