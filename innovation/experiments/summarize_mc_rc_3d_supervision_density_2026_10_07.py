"""Summarize authenticated label counts; no data loading, neural forward or training."""
import hashlib,json,statistics,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'experiments/mc_rc_3d_development_supervision_2026_10_07/attempt_01.json'
OUT=ROOT/'experiments/mc_rc_3d_supervision_density_2026_10_07'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def stats(values):
    return dict(n=len(values),min=min(values) if values else None,
                median=statistics.median(values) if values else None,max=max(values) if values else None)
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    source=json.loads(SOURCE.read_text(encoding='utf-8'));assert source['complete'] and not source['errors']
    assert source['development_patients']==11 and source['development_series']==19 and source['draws_checked']==608
    sizes=[1048576,131072,16384];rows=[];ratios=[[],[]];forced_fractions=[];batch_fractions=[]
    disappearing_uniform=[0,0];undefined=[0,0];forced_zero=[0,0]
    for series in source['series']:
        assert len(series['draws'])==32
        fractions=[];batch=[];local_ratios=[[],[]];local_disappearing=[0,0];local_undefined=[0,0]
        for draw in series['draws']:
            c=draw['patch_foreground_by_scale'];assert len(c)==3 and all(len(x)==2 for x in c)
            for counts,size,old_fraction in zip(c,sizes,draw['foreground_fraction_by_scale']):
                assert [n/size for n in counts]==old_fraction
            assert c[0][0]>0
            fractions.append(c[0][0]/sizes[0]);batch.append(sum(c[0])/(2*sizes[0]))
            for scale,factor in enumerate((2,4),start=1):
                k=scale-1;forced_zero[k]+=int(c[scale][0]==0)
                if c[0][1]>0 and c[scale][1]==0:
                    disappearing_uniform[k]+=1;local_disappearing[k]+=1
                for sample in (0,1):
                    if c[0][sample]==0:
                        assert c[scale][sample]==0;undefined[k]+=1;local_undefined[k]+=1
                    else:
                        relative=c[scale][sample]*factor**3/c[0][sample]-1
                        ratios[k].append(relative);local_ratios[k].append(relative)
        forced_fractions.extend(fractions);batch_fractions.extend(batch)
        rows.append(dict(patient=series['patient'],uid=series['uid'],physical_foreground=series['physical_foreground'],
                         forced_fine_fraction=stats(fractions),batch_fine_fraction=stats(batch),
                         relative_coarse_volume_error=[stats(v) for v in local_ratios],
                         uniform_fine_positive_coarse_zero=local_disappearing,empty_fine_patch_ratio_undefined=local_undefined))
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],series=rows,
                source_sha256=sha(SOURCE),script_sha256=sha(Path(__file__)),
                protocol_sha256=sha(ROOT/'MC_RC_3D_SUPERVISION_DENSITY_SUMMARY_PROTOCOL_2026-10-07.md'),
                development_patients=11,development_series=19,draws_summarized=608,
                forced_fine_fraction=stats(forced_fractions),batch_fine_fraction=stats(batch_fractions),
                relative_coarse_volume_error=[stats(v) for v in ratios],
                uniform_fine_positive_coarse_zero=disappearing_uniform,forced_positive_coarse_zero=forced_zero,
                empty_fine_patch_ratio_undefined=undefined,MR_source_pixels_decoded=0,label_values_newly_loaded=0,
                neural_forwards=0,actual_training_updates=0,actual_gpu_updates=0,
                scientific_confirmation_patients=0,publication_claim_confirmed=False,
                confirmation_patients_opened=False,validation_model_effects_opened=False,
                aggregation_scope='descriptive repeated draws; not independent patients or a causal test')
    with (OUT/'attempt01.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k!='series'},ensure_ascii=False))
if __name__=='__main__':main()
