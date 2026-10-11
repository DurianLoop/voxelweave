"""Bind current observed exits, actual reading scope, and live-training observations."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def new(p,r):
    with p.open('x',encoding='utf-8') as s:json.dump(r,s,ensure_ascii=False,indent=2);s.write('\n')
def entry(relative):
    p=ROOT/relative;assert p.is_file();return dict(path=relative,bytes=p.stat().st_size,sha256=sha(p))
def main():
    sys.stdout.reconfigure(encoding='utf-8');now=datetime.now(timezone.utc).isoformat()
    observed=[
        ('inherited_synthetic_workflow',0,'d6352c','experiments/mc_rc_3d_paired_resource_workflow_synthetic_2026_10_07/attempt01.json',True),
        ('synthetic_independent_verifier',0,'aec550','experiments/mc_rc_3d_paired_resource_workflow_synthetic_2026_10_07/independent_attempt01.json',False),
        ('inherited_real_CPU_deferred',3,'300d9f','experiments/mc_rc_3d_paired_real_resource_2026_10_07_cpu_attempt01/attempt01.json',True),
        ('workflow_exit_receipt',0,'0f4763','SESSION_OBSERVED_EXITS_PAIRED_RESOURCE_WORKFLOW_2026-10-07.json',False),
        ('cuda_v2_preparation',0,'84bd1c','experiments/mc_rc_3d_paired_resource_cuda_telemetry_v2_preparation_2026_10_07/attempt01.json',False),
        ('cuda_v2_GPU_entry_deferred',3,'c6e2b3','experiments/mc_rc_3d_paired_real_resource_v2_2026_10_07_gpu_attempt01/attempt01.json',False),
        ('ltt_ordering_counterexample',0,'eaedca','experiments/ltt_ordering_counterexample_cpu_2026_10_07/attempt01.json',False),
        ('ltt_ordering_independent_integer_verifier',0,'408954','experiments/ltt_ordering_counterexample_cpu_2026_10_07/independent_attempt01.json',False),
        ('inherited_LTT_acquisition',0,'bb7039','literature/source_cache/learn_then_test_primary_2026-10-07/download_extraction_attempt01.json',True),
        ('LTT_rendering',0,'93769f','literature/source_cache/learn_then_test_render_2026-10-07/render_attempt01.json',False),
        ('pareto_identity_failed_attempt01',1,'edeef8','literature/source_cache/pareto_testing_primary_2026-10-07/download_extraction_attempt01.json',False),
        ('pareto_venue_index_failed_attempt02',1,'ceac2b','literature/source_cache/pareto_testing_primary_recovery_2026-10-07/download_extraction_attempt02.json',False),
        ('pareto_official_title_search_attempt03',0,'a29af6','literature/source_cache/pareto_testing_official_search_2026-10-07/search_attempt03.json',False),
        ('pareto_verified_acquisition_attempt04',0,'6d0150','literature/source_cache/pareto_testing_verified_primary_2026-10-07/download_extraction_attempt01.json',False),
        ('pareto_rendering',0,'1f358a','literature/source_cache/pareto_testing_render_2026-10-07/render_attempt01.json',False)]
    exits={key:dict(observed_tool_exit=code,observed_tool_chunk=chunk,result=entry(path),
        observation_source='inherited_actual_tool_observation_from_user_handoff' if inherited else 'current_actual_exec_command_with_PowerShell_exit_forwarding')
        for key,code,chunk,path,inherited in observed}
    for key in ('pareto_identity_failed_attempt01','pareto_venue_index_failed_attempt02'):
        c=read(ROOT/exits[key]['result']['path']);assert not c['complete'] and c['errors'] and not c['reading_performed']
    for key in ('inherited_real_CPU_deferred','cuda_v2_GPU_entry_deferred'):
        c=read(ROOT/exits[key]['result']['path']);assert c['complete'] and c['status']=='prerequisite_deferred' and not c['errors']
        assert not c['neural_modules_imported'] and not c['CUDA_initialized'] and c['actual_resource_updates']==0
        assert c['MRI_observed_packages_loaded']==c['development_GT_loaded']==0
    c=read(ROOT/exits['cuda_v2_GPU_entry_deferred']['result']['path']);assert c['CUDA_initialization_observation_valid']
    papers=[];views=[]
    specs=[('learn_then_test','learn_then_test_primary_2026-10-07','download_extraction_attempt01.json','learn_then_test_render_2026-10-07',
        list(range(1,10))+list(range(11,16))+[22,23],list(range(1,10))+[11,12],[13,14,15,22,23],[2,3,4,5,6],35),
        ('pareto_testing','pareto_testing_verified_primary_2026-10-07','download_extraction_attempt01.json','pareto_testing_render_2026-10-07',
        list(range(1,10))+[13,14],[],list(range(1,10))+[13,14],[],23)]
    for key,directory,resultfile,renderdir,pages,inherited,added,reread,count in specs:
        folder=ROOT/'literature/source_cache'/directory;acq=read(folder/resultfile)
        assert acq['complete'] and not acq['errors'] and acq['physical_pages']==count
        assert not acq['reading_performed'] and not acq['visual_review_performed']
        pdf=entry(acq['pdf_file']);assert pdf['sha256']==acq['pdf_sha256']
        texts=[entry((folder/f'page{page:02d}.txt').relative_to(ROOT).as_posix())|dict(page=page) for page in pages]
        for t in texts:assert t['sha256']==next(x for x in acq['text_pages'] if x['page']==t['page'])['sha256']
        rr=ROOT/'literature/source_cache'/renderdir/'render_attempt01.json';render=read(rr)
        assert render['complete'] and render['pdf_sha256']==pdf['sha256'] and len(render['records'])==5
        for v in render['records']:
            assert sha(ROOT/v['file'])==v['sha256'] and not v['visual_review_performed'] and v['render_exit']==0
            views.append(dict(paper=key,**v,actual_view_image_executed=True,
                visual_observation_source='Current functions.exec view_image returned image blocks, visually inspected in this context.'))
        papers.append(dict(key=key,pdf=pdf,acquisition=entry((folder/resultfile).relative_to(ROOT).as_posix()),
            physical_PDF_pages=count,complete_selected_pages_read=pages,selected_page_files=texts,
            inherited_read_pages=inherited,newly_read_pages_this_context=added,reread_pages_this_context=reread,
            all_appendices_or_entire_paper_read=False))
    scope=dict(created_utc=now,complete=True,errors=[],script_sha256=sha(__file__),
        primary_papers_selected_read=2,successful_PDF_pages=58,complete_selected_unique_pages_read=27,
        selected_pages_newly_read_this_context=16,inherited_selected_pages=11,
        actual_visual_pages_reviewed=10,papers=papers,actual_source_visual_reviews=views,
        original_download_and_render_false_reading_flags_preserved=True,not_MRI_reproduction=True)
    new(ROOT/'literature/resource_and_ltt_reading_provenance_2026-10-07.json',scope)
    roots=[dict(path=str(ROOT.parent/name),sha256=sha(ROOT.parent/name)) for name in ('.gitignore','environment.yml')]
    progress=dict(created_utc=now,complete=True,errors=[],own_live_runs=[99542],full_training_observed_tool_exit=None,
        latest_actual_training_poll=dict(chunk='91cadc',native_updates=8514,invocation02_new_updates=8415,
            cumulative_wall_seconds=18653.062951699947,returned_session=99542),
        PCHIP99_is_historical_not_realtime=True,both_original_last19998_frozen=False,
        final_models_evaluated=False,publication_claim_confirmed=False,goal_status='active',
        latest_GPU_query=dict(chunk='42139e',timestamp_local='2026/10/07 21:00:41.825',free_MiB=1394,total_MiB=24455,utilization_percent=92),
        GPU_authorized=True,GPU_startup_required_free_bytes=8000000000,GPU_new_qualification_not_run=True,
        root_files_observed=roots,other_processes_enumerated=False,other_processes_modified=False,
        current_lesion_confirmation_patients=0,old_MIRA_MSValid84_confirmation_preserved=True,
        patient_roles=dict(development_patients=11,development_series=19,seen_validation_patients=4,seen_validation_series=9,
            unopened_confirmation_patients=8,unopened_confirmation_series=12,locked_IXI_test_unopened=True))
    new(ROOT/'SESSION_EXECUTION_PROGRESS_RESOURCE_AND_LTT_2026-10-07.json',progress)
    ledger=dict(created_utc=now,complete=True,errors=[],script_sha256=sha(__file__),observed_exits=exits,
        reading_scope=entry('literature/resource_and_ltt_reading_provenance_2026-10-07.json'),
        progress=entry('SESSION_EXECUTION_PROGRESS_RESOURCE_AND_LTT_2026-10-07.json'),
        stage_synthetic_workflow_updates=8,synthetic_updates_executed_in_current_context=0,
        independent_Numpy_training_batch_replays=6,independent_binary_outcomes=65536,
        new_MRI_pixels_loaded=0,new_development_GT_loaded=0,new_MRI_forwards=0,new_GPU_forwards=0,
        real19series_resource_qualification_completed=False,publication_claim_confirmed=False,goal_status='active',
        inspection_command_failure=dict(chunk='d9230d',observed_exit=1,
            reason='PowerShell python -c nested quotes lost; NameError innovation; changed to ConvertFrom-Json inspection, no scientific run.'),
        preserved_failures=['PMLR path 404','wrong arXiv ID title rejected before PDF download','PMLR206 index title absent'],
        scientific_limitations=['No independent replay of unsaved neural weights/probabilities',
            'GPU exception path not exercised','4 already-seen validation patients are not fresh calibration',
            'LTT/Pareto mechanisms and synthetic counterexample are prior art, not an MRI publication claim'])
    new(ROOT/'SESSION_EXECUTION_LEDGER_RESOURCE_AND_LTT_2026-10-07.json',ledger)
    print(json.dumps(dict(complete=True,observed_exits_bound=len(exits),selected_unique_pages=27,actual_visual_pages=10)));return 0
if __name__=='__main__':raise SystemExit(main())
