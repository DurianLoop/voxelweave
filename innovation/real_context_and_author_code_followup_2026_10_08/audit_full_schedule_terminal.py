"""After real terminal only: full journal audit and original sampler replay, no MRI."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import sys,json,gzip,time,gc,collections,itertools
from pathlib import Path
import numpy as np
import torch
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,dump,resource_guard
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_3d_19series_common_init_2026_10_07 import development_cases,lattice,physical_label,read_reference_label,sample_batch,batch_rng,array_sha
sys.path.insert(0,str(ROOT/'spatial_adaptation_matched_2026_10_08'))
from spatial_transform import primitives,pivots
def main():
    sys.stdout.reconfigure(encoding='utf-8');torch.set_num_threads(1);resource_guard();started=time.perf_counter()
    terminalpath=HERE/'ACTUAL_FULL_SCHEDULE_TERMINAL_TOOL.json';terminal=read(terminalpath)
    assert terminal['exit_code']==0 and 'session_id' not in terminal and terminal['observed_unified_exec_session']==56132
    live=HERE/'full_schedule_attempt01';r=read(live/'receipt.json');config=read(live/'frozen_config.json')
    assert r['complete'] and not r['errors'] and r['status']=='completed' and r['geometry_patches_completed']==5984
    assert r['all5984_geometry_targets_verified'] and r['frozen_config_sha256']==sha(live/'frozen_config.json')
    for b in r['source_bindings']:bind(b)
    jpath=ROOT/r['journal_path'];assert sha(jpath)==r['journal_sha256'] and jpath.stat().st_size==r['journal_bytes']
    with gzip.open(jpath,'rt',encoding='utf-8') as f:rows=[json.loads(line) for line in f]
    assert len(rows)==5984;indexed={(x['step'],x['patch']):x for x in rows}
    assert len(indexed)==len(rows) and set(indexed)==set(itertools.product(range(1,2993),range(2)))
    oldpath=ROOT/'vs_task_baseline_followup_2026_10_08/real_development_entry_attempt01/receipt.json';old={s['uid']:s for s in read(oldpath)['series']}
    parent=ROOT/'experiments/mc_rc_3d_19series_common_init_cpu_2026_10_07';parentconfig=read(parent/'frozen_config.json')
    schedule=np.load(parent/parentconfig['schedule_file'],allow_pickle=False)[:2992];assert array_sha(schedule)==config['schedule_prefix_sha256']
    exposures=collections.Counter();active=0;foreground_missing=0;foreground_exposure=0;fully=0;max_error=0.;max_coordinate=0.;case_steps=0
    cases=development_cases();assert len(cases)==19;GT_loaded=0
    def guard():
        resource_guard();assert time.perf_counter()-started<900 and not torch.cuda.is_initialized()
        assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    for ci,(c,_) in enumerate(cases):
        guard();grid=lattice(c);target=physical_label(read_reference_label(c),grid);GT_loaded+=1
        assert array_sha(target)==old[c['uid']]['physical_label_sha256']
        dummy=np.broadcast_to(np.array(0.,dtype=np.float32),target.shape)
        for ix in np.flatnonzero(schedule[:,1]==ci):
            guard();step=int(ix)+1;x,y,geometry=sample_batch(dummy,target,batch_rng(19998+step));del x
            piv=pivots(geometry,y.shape[2:]);prs=primitives(step);mother=array_sha(y.numpy());patient=parentconfig['patient_ids'][int(schedule[ix,0])]
            assert c['patient']==patient;exposures[patient]+=1;case_steps+=1
            for pi in range(2):
                row=indexed[(step,pi)];assert row['patient']==patient and row['uid']==c['uid']
                assert row['geometry']==geometry[pi] and row['pivot_zrc']==piv[pi] and row['primitive']==prs[pi]
                assert row['mother_label_sha256']==mother and row['target_label_sha256']==array_sha(y.numpy()[pi,0])
                assert row['all_target_voxels_verified'] and row['coordinate_max_error']<=3e-12 and row['support_max_error']<=3e-6 and row['binary_disagreements']==0
                s=row['support_stats'];ov=row['overlap'];assert s['voxels']==1048576 and 0<=s['fully_supported_fraction']<=1
                assert ov['foreground']['voxels']==int(y.numpy()[pi,0].sum()) and ov['foreground']['voxels']+ov['background']['voxels']==1048576
                assert ov['foreground']['incomplete_support_voxels']+ov['background']['incomplete_support_voxels']==1048576-s['fully_supported_voxels']
                expected=bool(prs[pi]['enabled'] and (prs[pi]['scale']!=1 or any(prs[pi]['degrees_xyz'])))
                assert row['active']==expected;active+=int(expected);foreground_missing+=ov['foreground']['incomplete_support_voxels'];foreground_exposure+=ov['foreground']['voxels']
                fully+=int(s['fully_supported_fraction']==1.);max_error=max(max_error,row['support_max_error']);max_coordinate=max(max_coordinate,row['coordinate_max_error'])
            del y
        del target,dummy;gc.collect()
    assert case_steps==2992 and len(exposures)==11 and set(exposures.values())=={272}
    assert active==r['active_patches_completed'] and foreground_missing==r['FG_incomplete_exposure_voxels'] and foreground_exposure==r['FG_exposure_voxels']
    assert fully==r['patches_entirely_supported'] and max_error==r['max_support_error'] and max_coordinate==r['max_coordinate_error']
    out=HERE/'full_schedule_audit_attempt01';out.mkdir(exist_ok=False)
    result=dict(complete=True,errors=[],observed_tool_exit=0,observed_unified_exec_session=56132,observed_terminal_chunk=terminal['chunk_id'],
        all5984_journal_rows_verified=True,all2992_original_sample_batch_geometry_and_mother_labels_matched=True,
        support_fields_not_reexecuted_in_this_audit=True,qualification_records_checked_against_all_strict_gates=True,
        development_patients=11,development_series=19,patient_step_exposures=dict(exposures),active_patches=active,
        FG_incomplete_exposure_voxels=foreground_missing,FG_exposure_voxels=foreground_exposure,fully_supported_patches=fully,
        GT_arrays_loaded=GT_loaded,MRI_arrays_loaded=0,checkpoint_arrays_loaded=0,patient_neural_forwards=0,training_updates=0,
        validation_pixels_loaded=False,confirmation_patients_opened=False,lockedIXI_opened=False,CUDA_initialized=torch.cuda.is_initialized(),
        source_bindings=[entry(p) for p in [Path(__file__),HERE/'FULL_SCHEDULE_TERMINAL_AUDIT_PROTOCOL.md',terminalpath,live/'receipt.json',live/'frozen_config.json',jpath]],
        elapsed_seconds=time.perf_counter()-started,publication_claim_confirmed=False,goal_status='active')
    dump(out/'receipt.json',result);guard();print(json.dumps({k:v for k,v in result.items() if k!='source_bindings'}),flush=True)
if __name__=='__main__':main()
