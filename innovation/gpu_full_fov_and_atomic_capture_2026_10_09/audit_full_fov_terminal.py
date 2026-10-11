"""Audit the ended full38 identities, complete voxel gates and actual atomic capture files."""
import itertools,json,math,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,dump,resource_guard
def main():
    started=time.perf_counter();resource_guard();tp=HERE/'ACTUAL_FULL_FOV_TERMINAL_TOOL.json';t=read(tp)
    assert t['exit_code']==0 and 'session_id' not in t
    rp=HERE/'full_fov_attempt01/receipt.json';r=read(rp);cfg=read(rp.with_name('frozen_config.json'))
    assert r['complete'] and r['status']=='completed' and not r['errors'] and r['all38_fullFOV_strict_numeric_gates_passed']
    assert r['frozen_config_sha256']==sha(rp.with_name('frozen_config.json'))
    assert r['MRI_arrays_loaded']==38 and r['GT_arrays_loaded']==r['training_updates']==0 and r['parent_model_arrays_loaded']==2
    for key in ['medical_effect_scored','validation_pixels_loaded','confirmation_patients_opened','lockedIXI_opened','other_PIDs_enumerated','other_PIDs_modified','original_training_modified','publication_claim_confirmed','training_ready']:assert not r[key],key
    for b in r['source_bindings']:bind(b)
    assert len(cfg['cases'])==19 and len({c['patient'] for c in cfg['cases']})==11
    identities=[(v['case'],v['kind']) for v in r['series']]
    assert len(identities)==len(set(identities))==38 and set(identities)==set(itertools.product(range(19),cfg['kinds']))
    maxima=[0.,0.];costs={};total_voxels=0
    for v in r['series']:
        assert v['complete'] and v['numeric_gate_passed'] and v['patient']==cfg['cases'][v['case']]['patient'] and v['uid']==cfg['cases'][v['case']]['uid']
        assert v['native_voxels']==math.prod(v['native_shape']) and v['native_voxels']>0;total_voxels+=v['native_voxels']
        assert 0<=v['max_probability_error']<=3e-6 and 0<=v['coordinate_max_error']<=3e-12 and v['binary_disagreements']==v['coordinate_binary_disagreements']==0
        assert v['GPU_binary_sha256']==v['CPU_binary_sha256']
        p=v['production_inference'];i=v['independent_inference'];assert p['full_fov'] and not p['label_used_for_inference']
        assert p['total_tiles']==i['total_tiles'] and p['axis_starts']==i['axis_starts'] and p['coverage_min']>0 and i['coverage_min']>0
        assert 0<v['GPU_peak_reserved_bytes']<=2_500_000_000
        maxima[0]=max(maxima[0],v['max_probability_error']);maxima[1]=max(maxima[1],v['coordinate_max_error'])
        for k,c in v['cost_seconds'].items():assert math.isfinite(c) and c>=0;costs[k]=costs.get(k,0)+c
    assert len(r['atomic_captures'])==2 and {c['kind'] for c in r['atomic_captures']}==set(cfg['kinds'])
    for c in r['atomic_captures']:
        assert c['reload_bitwise_equal'] and not c['power_failure_recovery_guaranteed'] and not c['optimizer_resume_supported'];bind(c['file'])
    assert r['elapsed_seconds']<10800 and r['resources_after']['GPU_free_bytes']>=4_000_000_000
    result=dict(complete=True,errors=[],all38_fullFOV_identities_and_entire_voxel_gates_verified=True,
        all_two_atomic_weight_files_source_hashes_verified=True,total_native_voxels=total_voxels,
        maximum_probability_coordinate_errors=maxima,all_binary_disagreements_zero=True,total_fullFOV_cost_seconds=costs,
        array_level_independent_FOV_rerun_in_this_audit=False,clinical_effect_confirmed=False,training_ready=False,publication_claim_confirmed=False,goal_status='active',
        source_bindings=[entry(p) for p in [Path(__file__),tp,rp,rp.with_name('frozen_config.json')]],resources=resource_guard(),elapsed_seconds=time.perf_counter()-started)
    out=HERE/'terminal_audit_attempt01';out.mkdir(exist_ok=False);dump(out/'receipt.json',result);print(json.dumps(result))
if __name__=='__main__':main()
