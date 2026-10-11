"""Bind measured results, literal tool exits, reading scopes, and unchanged roots."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),bytes=p.stat().st_size)
def new(p,r):
    with p.open('x',encoding='utf-8') as stream:json.dump(r,stream,ensure_ascii=False,indent=2);stream.write('\n')
def main():
    sys.stdout.reconfigure(encoding='utf-8');created=datetime.now(timezone.utc).isoformat()
    cost=ROOT/'experiments/mc_rc_observed_roi_cache_cost_v2_2026_10_07/attempt01.json'
    costproof=cost.parent/'independent_disk_rational_attempt01.json'
    probe=ROOT/'experiments/mc_rc_observed_roi_real_input_probe_2026_10_07/attempt01.json'
    failure=probe.parent/'independent_real_input_replay_attempt01.json'
    replay=probe.parent/'independent_real_input_replay_attempt02.json'
    docs=[read(p) for p in (cost,costproof,probe,replay)];assert all(d['complete'] and not d['errors'] and not d['prohibited_access_attempts'] for d in docs)
    assert docs[1]['checked_series']==16 and docs[1]['checked_method_supports']==64 and docs[1]['checked_plane_records']==3456
    assert docs[3]['checked_series']==16 and docs[3]['checked_candidates']==64 and docs[3]['checked_literal_tile_equalities']==4156
    f=read(failure);assert not f['complete'] and f['errors']==["KeyError: 'observed_array_sha256'"] and f['observed_MRI_packages_loaded']==1 and f['cached_prediction_arrays_loaded']==0
    observed_reads=docs[2]['observed_MRI_packages_loaded']+docs[3]['observed_MRI_packages_loaded']+f['observed_MRI_packages_loaded'];assert observed_reads==33
    cached_reads=sum(d['cached_prediction_arrays_loaded'] for d in docs)+f['cached_prediction_arrays_loaded'];assert cached_reads==256
    for a,b in zip(docs[0]['summaries'],docs[2]['summaries']):
        assert a['method']==b['method'] and a['recomputed_batch_pairs_total']==b['actual_recomputed_batch_pairs_total']==b['geometric_recomputed_batch_pairs_total']
        assert b['series_actual_k_less_than_geometric_k']==0
    source=ROOT/'literature/source_cache/temporal_cache_primary_2026-10-07'
    acquisition=read(source/'acquisition_attempt01.json');renders=read(source/'render_attempt01.json');assert len(acquisition['records'])==2 and all(v['complete'] and not v['errors'] for v in acquisition['records'])
    scopes=[]
    for v in acquisition['records']:
        assert v['physical_pages']==10
        pdf=ROOT/v['pdf_file'];assert sha(pdf)==v['pdf_sha256']
        pages=list(range(1,9 if v['key']=='skipconvs' else 10));texts=[x for x in v['page_texts'] if x['physical_page'] in pages]
        for x in texts:assert sha(ROOT/x['path'])==x['sha256']
        images=[entry(ROOT/x['path']) for x in renders if x['key']==v['key']]
        for x in renders:
            if x['key']==v['key']:assert x['render_exit']==0 and sha(ROOT/x['path'])==x['sha256'] and x['visually_reviewed'] is False
        scopes.append(dict(key=v['key'],PDF=entry(pdf),physical_text_pages_read=pages,page_texts=texts,
            physical_visual_pages_reviewed=[x['physical_page'] for x in renders if x['key']==v['key']],actual_visual_image_files=images,
            reference_pages_not_read=[9,10] if v['key']=='skipconvs' else [10],
            physical_page9_includes_partial_references=v['key']=='motiondelta',supplement_read=False,author_code_reproduced=False,
            read_tool_chunks=['56513f','1b62ad','b9a859'] if v['key']=='skipconvs' else ['cb22b0','e02852','069955','afa7ee'],
            actual_image_tool='tools.view_image through functions.exec',visual_tool_observed_success=True))
    provenance=ROOT/'literature/temporal_cache_reading_provenance_2026-10-07.json'
    new(provenance,dict(created_utc=created,complete=True,errors=[],source_bindings=[entry(x) for x in (Path(__file__),source/'acquisition_attempt01.json',source/'render_attempt01.json',ROOT/'literature/2026-10-07_temporal_cache_primary_protocol.md',ROOT/'literature/2026-10-07_temporal_cache_primary_reading.md')],
        acquisition_actual_tool_chunk='025e7a',acquisition_actual_tool_exit=0,render_actual_tool_chunk='c64cb2',render_actual_tool_exit=0,
        new_primary_papers_read=2,physical_PDF_pages_acquired=20,main_and_selected_page_texts_read=17,physical_pages_visual_reviewed=4,scopes=scopes,
        scope_is_actual_selected_reading_not_whole_PDF_claim=True))
    observations=ROOT/'SESSION_TOOL_OBSERVATIONS_OBSERVED_ROI_2026-10-07.json'
    exited=[('observed_roi_cost_v2',cost,'bba1ca',0),('observed_roi_cost_independent',costproof,'1a70af',0),
        ('real_input_probe',probe,'540786',0),('real_input_independent_failed_v1',failure,'80dc21',1),
        ('real_input_independent_v2',replay,'2ec36b',0),('temporal_papers_acquisition',source/'acquisition_attempt01.json','025e7a',0),
        ('temporal_key_pages_render',source/'render_attempt01.json','c64cb2',0)]
    receipts=[dict(key=k,**entry(p),actual_observed_tool_chunk=chunk,actual_observed_tool_exit=code) for k,p,chunk,code in exited]
    training=dict(session_id=99542,latest_actual_poll_chunk='8088b4',returned_same_live_session=True,full_training_observed_tool_exit=None,
        latest_update=dict(kind='native_reference',updates=11286,loss=0.17150664329528809,new_updates=11187,cumulative_wall_seconds=25168.02466809994),
        actual_live_polls=[dict(chunk='45559e',last_native_updates=10791),dict(chunk='e0b0e1',last_native_updates=10890),dict(chunk='d358cb',last_native_updates=11187),dict(chunk='8088b4',last_native_updates=11286)],
        poll_is_progress_not_model_benefit_evaluation=True,user_terminal_processes_not_controlled=True)
    new(observations,dict(created_utc=created,complete=True,errors=[],actual_exits=receipts,training=training,
        GPU=dict(actual_query_chunk='c452a1',actual_query_exit=0,timestamp='2026/10/07 22:46:50.217',free_MiB=1394,total_MiB=24455,utilization_percent=90,new_GPU8GB_margin_met=False),
        implementation_checks=[dict(chunk='08a7b9',exit=0,all16_grid_JSON_normalized_exact_equal=True,all16_tile_locations_exact_equal=True),
            dict(chunk='6c35b1',exit=0,created_cost_v2=True,v1_source_SHA_retained=True),dict(chunk='fe4f1f',exit=0,independent_failed_v1_traceback_read=True),
            dict(chunk='acb6c1',exit=0,created_real_input_independent_v2=True,failed_v1_retained=True)],
        read_only_command_failures=[dict(chunk='714b5b',actual_observed_tool_exit=1,reason='Second Get-Content used a non-existent guessed cache script; first observed-input loader was successfully read; discovered real script via rg --files and read at220e81.',scientific_result_failure=False)],
        imported_precompaction_events=[dict(chunk='e28394',reported_exit=1,source='user supplied handoff and preserved attempt01.json',event='Cost V1 grid assertion before prediction arrays'),
            dict(chunk='8ae6d2',reported_exit=1,source='user supplied handoff',event='PowerShell rg wildcard path read error'),
            dict(chunk='2260fa',reported_exit=1,source='user supplied handoff',event='Guessed prior prediction receipt absent; actual path recovered at b47576')],
        tool_record_scope='Actual meaningful exits/polls and result/source bindings; not a fabricated byte-for-byte export of unavailable tool protocol messages.'))
    previous=read(ROOT/'SESSION_EXECUTION_LEDGER_REAL_SUPPORT_2026-10-07.json');roots=[]
    for v in previous['root_files_observed']:
        p=Path(v['path']);assert sha(p)==v['sha256'];roots.append(dict(path=str(p),sha256=sha(p),previous_sha256=v['sha256'],unchanged=True))
    ledger=ROOT/'SESSION_EXECUTION_LEDGER_OBSERVED_ROI_2026-10-07.json'
    new(ledger,dict(created_utc=created,complete=True,errors=[],source_bindings=[entry(x) for x in (Path(__file__),cost,costproof,probe,failure,replay,observations,provenance)],
        actual_exits=receipts,root_files_observed=roots,new_primary_papers_read=2,main_and_selected_page_texts_read=17,visual_pages_reviewed=4,
        unique_development_patients=8,unique_development_series=16,current19_without_old_predictions=3,
        checked_cost_supports=64,checked_cost_plane_records=3456,checked_real_input_candidates=64,checked_literal_tile_equalities=4156,
        actual_observed_MRI_package_array_loads_including_failed_attempt=observed_reads,cached_prediction_array_loads=cached_reads,
        new_GT_array_loads=0,native_reference_MRI_array_loads=0,new_model_forwards=0,new_GPU_forwards=0,new_training_updates=0,
        original_running_training_updates_excluded_from_new_probe_counts=True,original_training=training,
        own_live_runs=[99542],validation_arrays_loaded=0,confirmation_patients_opened=False,current_lesion_confirmation_patients=0,
        publication_claim_confirmed=False,actual_MRI_risk_certificates_issued=0,old_MIRA_MSValid84_confirmation_preserved=True,
        clinical_benefit_measured=False,actual_deployment_speed_benchmarked=False,other_processes_modified=False,
        formal_final_budget_completed=False,original56FOV_evaluated=False,goal_status='active',previous_goal_turn_classification='progress',current_goal_turn_classification='progress'))
    print(json.dumps(dict(complete=True,new_primary_papers_read=2,selected_text_pages_read=17,visual_pages_reviewed=4,
        checked_cost_supports=64,checked_real_input_candidates=64,checked_literal_tile_equalities=4156,
        actual_observed_MRI_array_loads=33,new_GT_arrays=0,root_hashes_unchanged=True,goal_status='active',publication_claim_confirmed=False)),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
