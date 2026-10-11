"""Exactly enumerate clamped voxel-center sampling probabilities, without MRI or labels."""
import hashlib,json,math,sys
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments/mc_rc_3d_crop_origin_sampling_audit_2026_10_07'
SOURCE=ROOT/'experiments/mc_rc_3d_baseline_inputs_attempt02_2026_10_07/attempt_01.json'
PATCH=(64,128,128)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def axis_distribution(n,p):
    centers=np.arange(n);starts=np.clip(centers-p//2,0,n-p);frequency=np.bincount(starts,minlength=n-p+1)
    if n==p:expected=np.asarray([n],dtype=int)
    else:
        expected=np.ones(n-p+1,dtype=int);expected[0]=p//2+1;expected[-1]=p//2
    assert np.array_equal(frequency,expected) and frequency.sum()==n
    endpoints=frequency[0]+(frequency[-1] if len(frequency)>1 else 0)
    clamped=endpoints/n;uniform=min(2,len(frequency))/len(frequency)
    return dict(grid_n=n,patch_p=p,legal_origins=len(frequency),
        origin_counts=[int(v) for v in frequency],center_count=n,
        clamped_uniform_center_endpoint_probability=clamped,
        uniform_legal_origin_endpoint_probability=uniform,
        endpoint_probability_ratio=clamped/uniform)
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    data=json.loads(SOURCE.read_text(encoding='utf-8'));assert data['complete'] and not data['errors']
    rows=[]
    for series in data['series']:
        if series['role']!='development':continue
        shape=series['inputs']['raw_pchip']['physical_image_shape_zrc']
        axes=[axis_distribution(n,p) for n,p in zip(shape,PATCH)]
        variable=[a for a in axes if a['legal_origins']>1]
        rows.append(dict(patient=series['patient'],uid=series['uid'],shape_zrc=shape,axis_distributions=axes,
            probability_at_least_one_variable_axis_at_edge_under_clamped_centers=1-math.prod(1-a['clamped_uniform_center_endpoint_probability'] for a in variable),
            probability_at_least_one_variable_axis_at_edge_under_uniform_origins=1-math.prod(1-a['uniform_legal_origin_endpoint_probability'] for a in variable)))
    assert len(rows)==19 and len({r['patient'] for r in rows})==11
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],script_sha256=sha(__file__),
        source_file=SOURCE.relative_to(ROOT).as_posix(),source_sha256=sha(SOURCE),series=rows,
        comparison='Only the nominal uniform background crop origin rule is audited. Foreground-center sampling and trained model effects are not evaluated.',
        current_rule_has_boundary_atoms=True,alternative_is_uniform_legal_origin_sampling,
        candidate_trial_performed=False,current_training_protocol_modified=False,
        mr_or_label_values_loaded=0,neural_forwards=0,actual_gpu_updates=0,
        validation_effects_opened=False,confirmation_patients_opened=False,publication_claim_confirmed=False)
    path=OUT/'attempt01.json';path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(complete=True,series=19,example_001=rows[0]['axis_distributions'][1],neural_forwards=0)))
if __name__=='__main__':main()
