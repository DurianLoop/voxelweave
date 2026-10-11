"""Bind actual completed MRI qualification and all 3970 author-source lines."""
import sys, json, re, time
from pathlib import Path
from datetime import datetime, timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,dump,resource_guard
LIVE=[ROOT/'spatial_adaptation_matched_2026_10_08/training_attempt01',HERE/'full_schedule_attempt01']
def allowed(p):
    return all(not p.is_relative_to(d) or p==d/'frozen_config.json' for d in LIVE)

def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard();started=time.perf_counter()
    obs={}
    for p in sorted(HERE.glob('ACTUAL_TOOL_OBSERVATIONS_PART*.json')):
        for x in read(p)['entries']:
            assert x['available'];a=x['actual_tool_result'];a=a['value'] if a.get('status')=='fulfilled' else a
            obs[x['store_key']]=(a,p)
    def actual(key,chunk,exit_code=None,session=None):
        a,p=obs[key];assert a['chunk_id']==chunk
        if exit_code is not None:assert a['exit_code']==exit_code and 'session_id' not in a
        if session is not None:assert a['session_id']==session and 'exit_code' not in a
        return dict(store_key=key,chunk_id=chunk,exit_code=a.get('exit_code'),session_id=a.get('session_id'),observation_file=entry(p))
    old=HERE/'vinn_code_attempt02';new=HERE/'vinn_training_chain_attempt01'
    specs=[
      (old/'FastSurferCNN__models__interpolation_layer.py',650,[('turn25_code_read1_0','12d33a',1,240),('turn25_code_read2_0','9fbc0f',241,460),('turn25_code_read3_0','b5fec9',461,650)]),
      (old/'FastSurferCNN__models__networks.py',410,[('turn25_code_read1_1','fbcaf6',1,410)]),
      (old/'FastSurferCNN__data_loader__augmentation.py',481,[('turn25_code_read2_1','02cd50',1,240),('turn25_code_read3_1','7fee8d',241,481)]),
      (old/'FastSurferCNN__models__sub_module.py',820,[('turn25_code_submodule_read1_0','46c4c1',1,303),('turn25_code_submodule_read1_1','e59909',304,598),('turn25_code_submodule_read2','7a0719',599,820)]),
      (new/'FastSurferCNN__config__defaults.py',240,[('turn26_chain_read_defaults_loader','6a0da1',1,240)]),
      (new/'FastSurferCNN__data_loader__loader.py',176,[('turn26_chain_read_defaults_loader','6a0da1',1,176)]),
      (new/'FastSurferCNN__train.py',427,[('turn26_chain_read_train1','86719c',1,220),('turn26_chain_read_train2','4b17de',221,427)]),
      (new/'FastSurferCNN__data_loader__dataset.py',544,[('turn26_chain_read_dataset1','527dce',1,285),('turn26_chain_read_dataset2','59ab7b',286,544)])]
    for direction in ['axial','coronal','sagittal']:
        specs.append((new/f'FastSurferCNN__config__FastSurferVINN_{direction}.yaml',74,[('turn26_chain_read_configs','743fd0',1,74)]))
    files=[]
    for p,count,spans in specs:
        lines=p.read_text(encoding='utf-8').splitlines();assert len(lines)==count
        coverage=[];streams=[]
        for key,chunk,lo,hi in spans:
            a,_=obs[key];e=actual(key,chunk,exit_code=0)
            assert 'Warning: truncated' not in a['output'] and 'UnicodeEncodeError' not in a['output']
            normalized='\n'.join(a['output'].splitlines())
            exact='\n'.join(f'{i}: {lines[i-1]}' for i in range(lo,hi+1))
            assert exact in normalized,(p.name,lo,hi)
            coverage.extend(range(lo,hi+1));streams.append(dict(first_line=lo,last_line=hi,**e))
        assert coverage==list(range(1,count+1))
        files.append(dict(source=entry(p),lines=count,all_source_lines_actually_read=True,actual_untruncated_readings=streams))
    assert len(files)==11 and sum(x['lines'] for x in files)==3970
    real=read(HERE/'real_context_attempt02/receipt.json')
    assert real['complete'] and not real['errors'] and real['all76_real_MRI_fields_replayed']
    assert real['all76_previous_support_mask_SHA_matched'] and real['all76_original_labels_kept']
    assert real['max_intensity_error']<=3e-6 and real['max_support_error']<=3e-6
    for b in real['source_bindings']:bind(b)
    for p in [old/'receipt.json',new/'receipt.json']:
        r=read(p);assert r['complete'] and not r['errors']
        assert r['pinned_commit']=='550e84596b7adbc01bd0f2e93f1a127b1cb2df99'
        for record in r['records']:bind(record['source_binding'])
    root=read(ROOT/'full_support_oracle_and_vinn_followup_2026_10_08/READING_PROVENANCE.json')['root_file_bindings']
    for b in root:bind(b)
    sources=[p for p in HERE.rglob('*') if p.is_file() and allowed(p) and p.name not in ['READING_PROVENANCE.json','APPEND_INDEX.json','APPEND_PROOF.json']]
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        new_distinct_primary_maintexts_completed=0,previous_round_two_primary_maintexts_not_recounted=True,
        author_repository='Deep-MI/FastSurfer',pinned_commit='550e84596b7adbc01bd0f2e93f1a127b1cb2df99',
        author_files_actually_read=11,author_source_lines_actually_read=3970,author_files=files,
        author_implementation_executed=False,author_implementation_imported=False,author_training_reproduced=False,
        exact_2022_paper_training_version_not_qualified=True,
        first_context_failure=actual('turn25_real_context_start','eb79d9',exit_code=1),
        real_context_V2_actual_terminal=actual('turn25_terminal_and_schedule_0','563565',exit_code=0),
        first_API_failure=actual('turn25_vinn_code_start','e0096c',exit_code=1),
        pinned_author_code_acquisition=actual('turn25_vinn_advertisement_start','b9f50a',exit_code=0),
        training_chain_acquisition=actual('turn26_training_chain_fetch_and_polls_0','1c2de9',exit_code=0),
        real_MRI_input_arrays_loaded=38,GT_arrays_loaded=19,all76_real_MRI_fields_replayed=True,
        distinct_development_patients=11,development_series=19,distinct_geometry_patches=38,
        distinct_geometry_target_voxels=39845888,input_specific_intensity_voxels=79691776,
        max_intensity_error=real['max_intensity_error'],max_support_error=real['max_support_error'],
        new_checkpoint_arrays_loaded=0,new_patient_neural_forwards=0,new_training_updates=0,new_patient_medical_effects=0,
        full_schedule_support_currently_live=True,full_schedule_session=56132,full_schedule_medical_effects=0,
        latest_full_schedule_observation=actual('turn26_freeze_preflight_and_polls_1','a54ac5',session=56132),
        current_training_session=29823,current_training_frozen_device='cpu',actual_current_training_exit_observed=False,
        latest_training_observation=actual('turn26_freeze_preflight_and_polls_0','a260a1',session=29823),
        GPU_authorized=True,GPU_latest_observed_free_MiB=1394,new_GPU_start_reserve_MiB=8192,
        GPU_totals_actual=actual('turn26_protocol_and_resource_reads_3','1ed717',exit_code=0),
        ordinary_augmentation_training_ready=False,whole_patch_policy_only_prepared=True,
        new_validation_evaluation_executed=False,confirmation_patients_opened=False,lockedIXI_opened=False,
        support_is_unpadded_resampled_domain_not_observed_slice_certificate=True,
        support_mask_does_not_certify_task_output_independence=True,
        rolling_training_and_full_schedule_outputs_excluded=True,only_their_immutable_configs_bound=True,
        root_file_bindings=root,root_environment_and_gitignore_unchanged=True,
        dependencies_installed=False,agents_delegated=False,publication_claim_confirmed=False,goal_status='active',
        source_bindings=[entry(p) for p in sorted(sources)],elapsed_seconds=time.perf_counter()-started)
    dump(HERE/'READING_PROVENANCE.json',result)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    print(json.dumps({k:result[k] for k in ['complete','author_files_actually_read','author_source_lines_actually_read',
          'all76_real_MRI_fields_replayed','new_distinct_primary_maintexts_completed','new_patient_medical_effects',
          'full_schedule_support_currently_live','actual_current_training_exit_observed','goal_status']}),flush=True)

if __name__=='__main__':main()
