"""Actual tool exits, separate new reading and old reread scopes; no MRI array loads."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'literature/source_cache/downstream_feature_cost_primary_2026-10-08'


def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())


def read(p):return json.loads(p.read_text(encoding='utf-8'))


def new(p,d):
    with p.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    operations=[
        ('primary_discovery_and_supplement','literature/source_cache/downstream_feature_cost_primary_2026-10-08/acquisition_attempt01.json','cfa74c',0),
        ('prakash_author_manuscript','literature/source_cache/downstream_feature_cost_primary_2026-10-08/prakash_arxiv_attempt01/acquisition_attempt01.json','0ed60a',0),
        ('feature_measurement_launcher','experiments/deployment_observed_feature_cost_launch_2026_10_08/launch_attempt01.json','3a6af2',0),
        ('metadata_independent_check','experiments/deployment_observed_feature_cost_metadata_2026_10_08/attempt01.json','e07897',0),
        ('conditional_variance_step_check','experiments/conditional_variance_proof_step_2026_10_08/attempt01.json','f45139',0),
        ('render','literature/source_cache/downstream_feature_cost_primary_2026-10-08/visual_attempt01/render_attempt01.json','681ce7',0),
        ('cost_summary','experiments/deployment_feature_cost_summary_2026_10_08.json','ba6b1c',0),
        ('old_deferral_method_prepare_and_actual_read','literature/source_cache/downstream_feature_cost_primary_2026-10-08/old_deferral_method_reread_attempt01.json','88e05b',0)]
    exits=[dict(key=key,**entry(ROOT/path),actual_observed_tool_chunk=chunk,actual_observed_tool_exit=code,
        observation_source='direct_live_tool_result') for key,path,chunk,code in operations]
    primary=read(BASE/'acquisition_attempt01.json');prakash=read(BASE/'prakash_arxiv_attempt01/acquisition_attempt01.json')
    rendered=read(BASE/'visual_attempt01/render_attempt01.json')
    summary=read(ROOT/'experiments/deployment_feature_cost_summary_2026_10_08.json')
    assert all(v['complete'] and not v['errors'] for v in (primary,prakash,rendered,summary))
    supplement=[v for v in primary['records'] if v['key']=='noise2same_supplement'][0]
    assert supplement['physical_pages']==4 and prakash['physical_pages']==5
    assert prakash['identity']['arxiv_id'].endswith('1911.12239v3')
    assert summary['stage_medical_observed_package_load_events']==19
    for v in rendered['records']:assert not v['visually_reviewed']
    scopes=[dict(key='noise2same_supplement',PDF=supplement['file'],physical_pages_acquired=4,
        text_pages_read=[1,2,3,4],page_texts=supplement['page_texts'],visual_pages_reviewed=[1,2],
        supplemental_to_previous_paper=True,new_independent_paper=False,
        figure5_physical_page4_text_caption_read_but_image_not_viewed=True),
        dict(key='prakash_2020',PDF=prakash['records'][-1],physical_pages_acquired=5,text_pages_read=[1,2,3,4,5],
        page_texts=prakash['page_texts'],visual_pages_reviewed=[1,3],new_independent_paper=True,
        author_code_and_external_wiki_not_acquired_or_read=True)]
    for scope in scopes:
        assert entry(ROOT/scope['PDF']['path'])['sha256']==scope['PDF']['sha256']
        for v in scope['page_texts']:assert entry(ROOT/v['path'])['sha256']==v['sha256']
    old=read(BASE/'old_deferral_method_reread_attempt01.json')
    assert old['complete'] and all(not v['text_actually_reread'] for v in old['records'])
    oldtxt=ROOT/'literature/extracted/SafeRestore_2026.txt'
    provenance=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[entry(Path(__file__)),entry(BASE/'acquisition_attempt01.json'),
            entry(BASE/'prakash_arxiv_attempt01/acquisition_attempt01.json'),
            entry(BASE/'visual_attempt01/render_attempt01.json'),entry(BASE/'old_deferral_method_reread_attempt01.json'),
            entry(oldtxt),entry(ROOT/'literature/2026-10-08_downstream_segmentation_and_proof_reading.md'),
            entry(ROOT/'literature/2026-10-08_relative_utility_collision_recheck.md')],
        scopes=scopes,new_primary_papers_read=1,previous_paper_supplemental_documents_read=1,
        acquired_new_primary_and_supplemental_physical_pages=9,new_primary_and_supplemental_text_pages_read=9,
        visual_pages_reviewed=4,actual_visual_image_files=rendered['records'],
        actual_visual_observation='four successful tools.view_image direct outputs inspected',image_tool_chunk_identifier_returned=False,
        new_text_tool_chunks=['278229','307c86','6dfdf2'],
        old_primary_method_page_reread_count=2,old_method_actual_read_tool_chunk='88e05b',
        old_primary_method_reread_scopes=[dict(key=v['key'],physical_page=v['physical_page']) for v in old['records']],
        SafeRestore_actual_read_tool_chunk='90d225',SafeRestore_text_ranges_1based=[[347,401],[1265,1277]],
        prior_MoEDiff_excerpt_output_truncated_not_counted_as_complete_reread=True,
        truncated_search_or_excerpt_chunks=['4862a1','f08ac7'],
        author_training_reproduced=False,old_reading_and_acquisition_receipts_not_rewritten=True,
        supplemental_pdf_extraction_warning='Ignoring wrong pointing object 19 0 (offset 0)',
        other_two_Crossref_titles_are_metadata_only_not_new_papers=True,
        EuropePMC_zero_hits_is_not_absence_proof=True)
    provenance_path=ROOT/'literature/deployment_feature_cost_reading_provenance_2026-10-08.json'
    new(provenance_path,provenance)
    roots=[]
    for name,digest in (('.gitignore','7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524'),
        ('environment.yml','dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257')):
        p=ROOT.parent/name;assert hashlib.sha256(p.read_bytes()).hexdigest()==digest
        roots.append(dict(path=str(p),sha256=digest,previous_sha256=digest,unchanged=True))
    obs=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],actual_exits=exits,
        feature_measurement_live_launch=dict(chunk='70e946',session=90875,terminal_chunk='3a6af2',exit=0),
        direct_training_polls=[dict(chunk='18fc70',session=99542,native_updates=17622,new_updates=17523,cumulative_wall_seconds=40049.99794589996),
            dict(chunk='a5534f',session=99542,native_updates=17919,new_updates=17820,cumulative_wall_seconds=40726.84348219994),
            dict(chunk='6ab943',session=99542,native_updates=18216,new_updates=18117,cumulative_wall_seconds=41426.71797919995)],
        training_handle_still_live=True,full_training_observed_tool_exit=None,
        latest_GPU=dict(chunk='4f50f8',actual_observed_tool_exit=0,timestamp='2026/10/08 03:17:31.953',
            free_MiB=1394,total_MiB=24455,utilization_percent=89,new_GPU8GB_margin_met=False),
        automatic_approval_review_rejections_received=0,escalated_public_GET_invocation_chunks=['cfa74c','0ed60a'],
        TLS_certificate_verification_disabled=False,MRI_environment_modified=False,
        training_restarted=False,training_migrated=False,user_terminal_processes_controlled=False,
        other_processes_enumerated=False,new_agents_delegated=False,
        used_skill='pdf:pdf',PDF_use_read_only_no_authoring=True)
    obs_path=ROOT/'SESSION_TOOL_OBSERVATIONS_DEPLOYMENT_FEATURE_COST_2026-10-08.json'
    new(obs_path,obs)
    ledger=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[entry(Path(__file__)),entry(obs_path),entry(provenance_path)]+[entry(ROOT/p) for k,p,c,e in operations],
        actual_exits=exits,root_files_observed=roots,unique_development_patients=11,unique_development_series=19,
        observed_package_load_events=19,real_folds_executed=38,feature_count=17,feature_rows_exact=19,
        independent_metadata_aggregation_passed=True,independent_timing_repeated=False,
        measured_cold_child_end_to_end_seconds=summary['measured_cold_child_end_to_end_seconds'],
        measured_production_phase_subset_seconds=summary['measured_production_phase_subset_seconds'],
        new_metadata_and_variance_check_medical_array_loads=0,neural_forwards=0,GPU_forwards=0,training_updates=0,model_arrays_loaded=0,
        original_live_training_excluded_from_array_and_compute_counts=True,
        new_primary_papers_read=1,previous_paper_supplemental_documents_read=1,
        new_text_pages_read=9,visual_pages_reviewed=4,old_primary_method_pages_reread=2,
        conditional_variance_step_diagnostic_passed=True,complete_Noise2Same_theorem1_disproved=False,
        relative_utility_is_known_cost_sensitive_selection=True,two_path_cost_sensitive_defer_control_required=True,
        latest_training_poll=obs['direct_training_polls'][-1],latest_GPU=obs['latest_GPU'],
        original_training_session=99542,full_training_observed_tool_exit=None,
        formal_final_budget_completed=False,original56FOV_evaluated=False,all6_final_capability_gates_completed=False,
        actual_MRI_task_benefit_measured=False,full_action_cost_measured=False,real_task_latency_measured=False,
        actual_MRI_risk_certificates_issued=0,native_GT_validation_confirmation_pixels_read=False,
        confirmation_patients_opened=False,validation_data_read=False,locked_IXI_opened=False,
        old_MIRA_MSValid84_confirmation_preserved=True,goal_status='active',publication_claim_confirmed=False,
        current_goal_turn_classification='progress',previous_goal_turn_classification='progress',stage_max_saved_bytes=30_000_000)
    new(ROOT/'SESSION_EXECUTION_LEDGER_DEPLOYMENT_FEATURE_COST_2026-10-08.json',ledger)
    print(json.dumps(dict(complete=True,observed_package_load_events=19,cold_child_seconds=ledger['measured_cold_child_end_to_end_seconds'],
        new_primary_papers_read=1,new_supplemental_documents_read=1,new_text_pages_read=9,visual_pages_reviewed=4,
        old_method_pages_reread=2,native_updates=18216,full_training_exit=None,goal_status='active'),ensure_ascii=False),flush=True)
    return 0


if __name__=='__main__':raise SystemExit(main())
