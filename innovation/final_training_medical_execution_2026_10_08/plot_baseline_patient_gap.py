"""Patient-first baseline plot using frozen score JSON only; no MRI/GT/model arrays."""
import hashlib,json,sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    resource_guard();p=ROOT/'final_training_medical_execution_2026_10_08/precision_v4_attempt01/receipt.json'
    q=json.loads(p.read_text());assert q['complete'] and q['all_old_metrics_identical'] and not q['all_arms_validation_gates_passed']
    fig,axs=plt.subplots(1,2,figsize=(10,4),gridspec_kw={'width_ratios':[2.2,1]},sharey=True,layout='constrained')
    values=[]
    colors=['#2468A0','#D56E35']
    for ax,role,label in zip(axs,['development','validation'],['Development (11 patients / 19 series)','Seen validation (4 patients / 9 series)']):
        aa=[a[role+'_aggregate'] for a in q['arms']];patients=sorted(aa[0]['patients'])
        for i,patient in enumerate(patients):
            ys=[a['patients'][patient]['metrics']['full']['dice'] for a in aa]
            ax.plot([i-.12,i+.12],ys,color='#AAB0B6',lw=1,zorder=1)
        for j,(arm,a,color) in enumerate(zip(q['arms'],aa,colors)):
            v=[a['patients'][p]['metrics']['full']['dice'] for p in patients];mean=sum(v)/len(v)
            ax.scatter([i+(-.12 if j==0 else .12) for i in range(len(v))],v,c=color,s=38,label=arm['kind'].replace('_',' '),zorder=2)
            ax.axhline(mean,color=color,linestyle='--',lw=1,alpha=.7)
            values.append(dict(role=role,kind=arm['kind'],patient_means=dict(zip(patients,v)),mean=mean))
        ax.set_xticks(range(len(patients)),[p.rsplit('-',1)[-1] for p in patients]);ax.set_title(label,fontsize=11)
        ax.set_xlabel('Patient ID');ax.set_ylim(0,1);ax.grid(axis='y',alpha=.2);ax.spines[['top','right']].set_visible(False)
    axs[0].set_ylabel('Full FOV Dice (series mean within patient)');axs[0].legend(loc='lower left',frameon=False,fontsize=9)
    fig.suptitle('Final parent models: development fit does not establish generalization',fontsize=12)
    for suffix in ['png','svg']:
        dest=HERE/('BASELINE_PATIENT_GAP.'+suffix);assert not dest.exists();fig.savefig(dest,dpi=160)
    plt.close(fig)
    receipt=dict(complete=True,source_file=p.relative_to(ROOT).as_posix(),source_sha256=sha(p),values=values,
        medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,
        confidence_intervals_drawn=False,validation_is_independent_confirmation=False,publication_claim_confirmed=False,
        artifacts=[dict(path=x.relative_to(ROOT).as_posix(),sha256=sha(x)) for x in [HERE/'BASELINE_PATIENT_GAP.png',HERE/'BASELINE_PATIENT_GAP.svg']])
    with (HERE/'BASELINE_PATIENT_GAP_RECEIPT.json').open('x',encoding='utf-8') as f:json.dump(receipt,f,indent=2);f.write('\n')
    print(json.dumps(dict(complete=True,patients_plotted=15,source_sha256=sha(p))))
if __name__=='__main__':main()
