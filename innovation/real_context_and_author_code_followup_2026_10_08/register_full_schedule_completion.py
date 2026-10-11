"""Append completion provenance only after all real terminal, replay and policy analysis."""
import sys,time,json
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,dump,resource_guard

def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard();started=time.perf_counter()
    terminal=read(HERE/'ACTUAL_FULL_SCHEDULE_TERMINAL_TOOL.json')
    assert terminal['exit_code']==0 and 'session_id' not in terminal and terminal['observed_unified_exec_session']==56132
    r=read(HERE/'full_schedule_attempt01/receipt.json')
    audit=read(HERE/'full_schedule_audit_attempt01/receipt.json')
    policy=read(HERE/'whole_patch_policy_attempt01/receipt.json')
    for v in [r,audit,policy]:
        assert v['complete'] and not v['errors']
        for b in v['source_bindings']:bind(b)
    assert r['geometry_patches_completed']==5984 and audit['all5984_journal_rows_verified']
    assert audit['all2992_original_sample_batch_geometry_and_mother_labels_matched']
    assert set(audit['patient_step_exposures'].values())=={272} and len(audit['patient_step_exposures'])==11
    observations={}
    for p in sorted(HERE.glob('*TOOL_OBSERVATIONS*.json')):
        v=read(p)
        for x in v.get('entries',[]):
            a=x['actual_tool_result'];a=a['value'] if a.get('status')=='fulfilled' else a
            observations[x['store_key']]=(a,p)
    def actual(key):
        a,p=observations[key];assert a['exit_code']==0 and 'session_id' not in a
        return dict(store_key=key,chunk_id=a['chunk_id'],exit_code=0,observation_file=entry(p))
    records=[actual(key) for key in ['turn26_full_schedule_audit_terminal','turn26_whole_patch_policy_terminal']]
    source=HERE/'lesion_ranker_source_attempt01/ranker.py';lines=source.read_text(encoding='utf-8').splitlines();assert len(lines)==162
    a,p=observations['turn26_ranker_source_full_read']
    assert a['exit_code']==0 and 'Warning: truncated' not in a['output']
    assert '\n'.join(f'{i}: {line}' for i,line in enumerate(lines,1)) in '\n'.join(a['output'].splitlines())
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        primary_maintexts_newly_completed=0,FastSurfer_source_lines_previously_read=3970,ranker_source_lines_newly_read=162,
        ranker_reading=actual('turn26_ranker_source_full_read'),total_author_source_lines_actually_read=4132,
        full_schedule_actual_terminal=entry(HERE/'ACTUAL_FULL_SCHEDULE_TERMINAL_TOOL.json'),actual_followup_terminals=records,
        all5984_geometry_targets_verified=True,all2992_original_sampler_labels_and_geometry_matched=True,
        development_patients=11,development_series=19,active_patches=r['active_patches_completed'],
        geometry_target_exposure_voxels=r['geometry_target_exposure_voxels'],
        FG_incomplete_exposure_voxels=r['FG_incomplete_exposure_voxels'],FG_exposure_voxels=r['FG_exposure_voxels'],
        FG_exposure_fraction_incomplete=r['FG_incomplete_exposure_voxels']/r['FG_exposure_voxels'],
        max_support_error=r['max_support_error'],max_coordinate_error=r['max_coordinate_error'],
        policy_counts=policy['totals'],ordinary_augmentation_training_ready=False,
        full_schedule_GT_arrays_loaded=r['GT_arrays_loaded'],replay_audit_GT_arrays_loaded=audit['GT_arrays_loaded'],
        new_MRI_arrays_loaded=0,new_checkpoint_arrays_loaded=0,new_patient_neural_forwards=0,new_training_updates=0,new_patient_medical_effects=0,
        old_four_arm_training_still_pending=True,validation_evaluation_executed=False,confirmation_patients_opened=False,lockedIXI_opened=False,
        author_code_executed=False,publication_claim_confirmed=False,goal_status='active',
        source_bindings=[entry(q) for q in [Path(__file__),HERE/'full_schedule_attempt01/receipt.json',
            HERE/'full_schedule_audit_attempt01/receipt.json',HERE/'whole_patch_policy_attempt01/receipt.json',
            HERE/'LESION_RANKER_FINDINGS_POST_ARCHIVE.md',source]],elapsed_seconds=time.perf_counter()-started)
    dump(HERE/'FULL_SCHEDULE_COMPLETION_PROVENANCE.json',result)
    assert sum(q.stat().st_size for q in HERE.rglob('*') if q.is_file())<5_000_000
    print(json.dumps({k:v for k,v in result.items() if k not in ['source_bindings','ranker_reading','actual_followup_terminals']}),flush=True)

if __name__=='__main__':main()
