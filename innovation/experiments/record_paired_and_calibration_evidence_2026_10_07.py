"""Bind actual observed exits, reading scope, and live session observations."""
import hashlib,json,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def row(relative):
    p=ROOT/relative;assert p.is_file();return dict(path=relative,bytes=p.stat().st_size,sha256=sha(p))
def new(relative,data):
    with (ROOT/relative).open('x',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    primary='literature/source_cache/calibration_selection_primary_2026-10-07'
    recovery='literature/source_cache/calibration_selection_pmlr_attempt02_2026-10-07'
    initial=read(ROOT/primary/'download_extraction_attempt01.json');retry=read(ROOT/recovery/'download_extraction_attempt02.json')
    assert not initial['complete'] and retry['complete']
    papers=[]
    for key,n,pages,source in [('calibration',10,list(range(1,9)),retry),('selectivenet',9,list(range(1,8)),retry),
                              ('conformal_risk',19,list(range(1,9)),initial)]:
        p=next(x for x in source['records'] if x['key']==key);assert p['success'] and p['physical_pages']==n
        assert p['pdf_sha256']==sha(ROOT/p['pdf_file'])
        texts=[x for x in p['text_pages'] if x['page'] in pages]
        assert len(texts)==len(pages)
        for t in texts:assert t['sha256']==sha(ROOT/t['file'])
        papers.append(dict(key=key,title=p['expected_title'],pdf=row(p['pdf_file']),physical_pages=n,
            complete_text_pages_actually_read=pages,text_page_files=texts,
            entire_PDF_read=False,author_experiments_reproduced=False,
            version='arXiv2208.02814v4_2025-06-13' if key=='conformal_risk' else 'official_PMLR_conference_PDF'))
    render=read(ROOT/'literature/source_cache/calibration_selection_render_2026-10-07/render_attempt01.json')
    visuals=[]
    for v in render['records']:
        assert sha(ROOT/v['file'])==v['sha256']
        visuals.append(dict(**v,actual_view_image_executed=True,review_basis='actual_tool_images_seen_this_continuation'))
    provenance=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],papers=papers,
        new_primary_papers_method_and_results_read=3,successful_PDF_pages=38,selected_complete_pages_actually_read=23,
        actual_visual_pages_reviewed=7,actual_source_visual_reviews=visuals,
        initial_download_reading_flags_not_rewritten=True,CRC_fifth_author_corrected_to='Tal Schuster',
        CRC_experiment_is_gut_polyp_not_brain_MRI=True,remaining_reference_appendix_pages_not_fully_read=True)
    new('literature/source_cache/calibration_selection_render_2026-10-07/reading_provenance.json',provenance)
    events={
        'inherited_paired_sampling_FOV':('3e7ef8',0,61161,'experiments/mc_rc_3d_paired_sampling_fov_qualification_2026_10_07/attempt01.json',True),
        'inherited_coordinate_diagnostic':('f9749d',0,79318,'experiments/mc_rc_3d_two_channel_coordinate_diagnostic_2026_10_07/attempt01.json',True),
        'inherited_readiness_exit_forwarding_failed':('47847f',1,None,'experiments/mc_rc_3d_paired_resource_readiness_2026_10_07/attempt01.json',True),
        'inherited_readiness_expected_deferred':('ef9927',3,None,'experiments/mc_rc_3d_paired_resource_readiness_2026_10_07/attempt02.json',True),
        'primary_download_strict_HTTP_identity_failure':('7c096e',1,10740,primary+'/download_extraction_attempt01.json',False),
        'PMLR_HTTP_canonical_HTTPS_transport_recovery':('d1babf',0,None,recovery+'/download_extraction_attempt02.json',False),
        'synthetic_calibrated_risk_vs_gain':('3d4d86',0,None,'experiments/calibrated_risk_vs_action_gain_2026_10_07/attempt01.json',False),
        'independent_integer_Fraction_routing_verification':('7afe05',0,None,'experiments/calibrated_risk_vs_action_gain_2026_10_07/independent_attempt01.json',False),
        'source_page_renders':('0628b9',0,None,'literature/source_cache/calibration_selection_render_2026-10-07/render_attempt01.json',False),
        'synthetic_calibration_placement_with_Decimal':('6be8ff',0,None,'experiments/calibration_position_cpu_2026_10_07/attempt01.json',False),
    }
    observed={k:dict(chunk=c,observed_tool_exit=e,session=s,result=row(p),inherited_summary_and_bound_result=i)
        for k,(c,e,s,p,i) in events.items()}
    for k in ('synthetic_calibrated_risk_vs_gain','independent_integer_Fraction_routing_verification','synthetic_calibration_placement_with_Decimal'):
        p=read(ROOT/observed[k]['result']['path']);assert p['complete'] and not p['errors']
    coord=read(ROOT/observed['inherited_coordinate_diagnostic']['result']['path'])
    assert coord['all_float32_and_float64_coordinate_replays_passed'] and not coord['all_original_ideal_absolute_gates_passed']
    assert next(x for x in coord['arms'] if x['kind']=='direct')['original_ideal_coordinate_absolute_gate'] is False
    prior_progress=read(ROOT/'SESSION_EXECUTION_PROGRESS_DIRECT_OBSERVED_2026-10-07.json')
    roots=[]
    for old in prior_progress['root_files_observed']:
        assert sha(old['path'])==old['sha256'];roots.append(dict(**old,still_matches_prior_checkpoint=True))
    progress=dict(created_utc=datetime.now(timezone.utc).isoformat(),own_live_runs=[99542],full_training_observed_tool_exit=None,
        latest_observed_training_poll=dict(chunk='05cd6a',kind='native_reference',updates=7326,new_updates=7227,
            cumulative_wall_seconds=15863.582562200027,returned_session_id=99542,terminal_exit_observed=False),
        earlier_observed_training_polls=[dict(chunk='9e00ad',last_native=6831),dict(chunk='fd3b5b',last_native=7029),
            dict(chunk='c079eb',new_output=False),dict(chunk='9b569d',last_native=7128)],
        PCHIP99_is_historical_not_realtime=True,
        GPU_totals_observation=dict(chunk='a178d3',timestamp_local='2026/10/07 20:05:32.904',free_MiB=1394,total_MiB=24455,
            utilization_percent=90,new_GPU_start_floor_bytes=8000000000,new_GPU_started=False),
        root_files_observed=roots,formal_training_device_precision_recipe_changed=False,
        current_continuation_MRI_data_reads=0,current_continuation_MRI_forwards=0,current_continuation_training_updates=0,
        inherited_synthetic_updates_archived=6,inherited_neural_forwards_repeated_this_continuation=0,
        MRI_real_two_channel_resource_qualification_implemented=False,MRI_real_two_channel_resource_qualification_executed=False,
        eight_confirmation_and_locked_IXI_closed=True,other_processes_modified=False,delegated_agents=0,
        current_3D_lesion_confirmation_patients=0,whole_project_confirmation_zero_not_claimed=True,
        publication_claim_confirmed=False,final_execution_closed=False,goal_status='active')
    new('SESSION_EXECUTION_PROGRESS_PAIRED_AND_CALIBRATION_2026-10-07.json',progress)
    ledger=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],script_sha256=sha(__file__),observed_exits=observed,
        reading_scope=provenance,training_progress_file='SESSION_EXECUTION_PROGRESS_PAIRED_AND_CALIBRATION_2026-10-07.json',
        auxiliary_read_errors_preserved=[dict(chunk='2588c3',issue='PowerShell literal wildcard path invalid; literature search still ran'),
            dict(chunk='188774',issue='wrong filename mc_rc_3d_19series_common_init_cpu_2026_10_07.py; correct source read in c614b2'),
            dict(chunk='5e11f4/1360dd',issue='combined display truncated SelectiveNet pages2-4; reread pages2-3 in34c927 and4-5 in303b74')],
        missing_user_history_not_reconstructed=True,original_strict_direct_failure_preserved=True,
        new_publication_claim_confirmed=False,goal_status='active')
    new('SESSION_EXECUTION_LEDGER_PAIRED_AND_CALIBRATION_2026-10-07.json',ledger)
    print(json.dumps(dict(complete=True,primary_papers_read=3,selected_pages=23,visual_pages=7,live_session=99542,
        training_terminal_exit=None,new_MRI_forwards=0)));return 0
if __name__=='__main__':raise SystemExit(main())

