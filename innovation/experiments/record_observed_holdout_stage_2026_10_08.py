"""Record direct observations separately from the user-supplied imported handoff."""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'literature/source_cache/blindspot_dependence_primary_2026-10-08'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def entry(p):
    return dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size, sha256=sha(p))


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def new(p,d):
    with p.open('x',encoding='utf-8') as f:
        json.dump(d,f,ensure_ascii=False,indent=2)
        f.write('\n')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    handoff = ROOT/'SESSION_IMPORTED_HANDOFF_OBSERVED_HOLDOUT_2026-10-08.md'
    imported = [
        ('freeze','experiments/observed_holdout_feature_preregistration_2026_10_08.json','d8ade8',0),
        ('production','experiments/observed_holdout_feature_qualification_2026_10_08/attempt01.json','aad9d0',0),
        ('independent_failed','experiments/observed_holdout_feature_independent_2026_10_08/attempt01.json','628031',1),
        ('v2_prepare','experiments/observed_holdout_feature_layout_v2_preregistration_2026_10_08.json','1ff85d',0),
        ('v2_independent','experiments/observed_holdout_feature_independent_layout_v2_2026_10_08/attempt01.json','3a3097',0),
        ('acquisition_prepare','literature/prepare_blindspot_dependence_acquisition_2026_10_08.py','a331fc',0),
        ('initial_acquisition','literature/source_cache/blindspot_dependence_primary_2026-10-08/acquisition_attempt01.json','2a0b9a',0),
        ('openalex_429','literature/lookup_noise2same_identity_2026_10_08.py','4cd0eb',1),
        ('official_identity','literature/source_cache/blindspot_dependence_primary_2026-10-08/noise2same_official_identity_attempt01.json','0a665e',0),
        ('official_prepare','literature/prepare_noise2same_official_acquisition_2026_10_08.py','99349f',0),
        ('official_cap_failure','literature/source_cache/blindspot_dependence_primary_2026-10-08/noise2same_official_attempt01/acquisition_attempt01.json','a02665',1),
        ('response_probe','literature/diagnose_noise2same_public_response_2026_10_08.py','a8f10e',0),
        ('official_v2_prepare','literature/prepare_noise2same_official_acquisition_v2_2026_10_08.py','1f1f2c',0),
        ('official_pdfinfo_failure','literature/source_cache/blindspot_dependence_primary_2026-10-08/noise2same_official_attempt02/acquisition_attempt02.json','0cd39c',1),
        ('reader_v1_failure','literature/install_portable_blindspot_pdf_reader_2026_10_08.py','fb1b24',1)]
    direct = [
        ('reader_v2_failure','tools/blindspot_pdf_reader_v2_2026_10_08/installation_attempt02.json','4f7373',1),
        ('reader_v3_success','tools/blindspot_pdf_reader_v3_2026_10_08/installation_attempt03.json','62ac3c',0),
        ('extraction_and_render','literature/source_cache/blindspot_dependence_primary_2026-10-08/portable_extraction_render_attempt01/extraction_render_attempt01.json','daf7df',0),
        ('summary_metadata_key_failure','experiments/summarize_observed_holdout_feature_2026_10_08.py','a1d4b6',1),
        ('summary_v2','experiments/observed_holdout_feature_summary_2026_10_08.json','95544f',0)]
    exits = [dict(key=key,**entry(ROOT/path),actual_observed_tool_chunk=chunk,actual_observed_tool_exit=code,
        observation_source='user_supplied_handoff' if sequence is imported else 'direct_live_tool_result')
        for sequence in (imported,direct) for key,path,chunk,code in sequence]
    summary = read(ROOT/'experiments/observed_holdout_feature_summary_2026_10_08.json')
    table = read(ROOT/'experiments/observed_holdout_feature_table_2026_10_08.json')
    assert summary['complete'] and not summary['errors'] and summary['stage_medical_observed_package_load_events']==41
    assert len(table['rows'])==19 and len(table['feature_names'])==17
    assert all(v['MRI_task_labels'] is None and v['action_utility_labels'] is None and v['full_action_cost'] is None for v in table['rows'])
    extraction = read(BASE/'portable_extraction_render_attempt01/extraction_render_attempt01.json')
    assert extraction['complete'] and not extraction['errors']
    scopes = []
    for p in extraction['records']:
        selected = list(range(1,9)) if p['key']=='noise2void' else list(range(1,12))
        texts = ([dict(physical_page=i,**entry(BASE/f'noise2void_page{i:02d}.txt')) for i in selected]
                 if p['key']=='noise2void' else [v for v in p['page_texts'] if v['physical_page'] in selected])
        visuals = p['rendered_pages']
        assert all(not v['visually_reviewed'] for v in visuals)
        assert all(sha(ROOT/v['path'])==v['sha256'] for v in [p['PDF'],*texts,*visuals])
        scopes.append(dict(key=p['key'],PDF=p['PDF'],physical_pages_acquired=p['physical_pages'],
            text_physical_pages_read=selected,actual_page_texts=texts,
            text_read_observation_source='imported_prior_text_tool_reads' if p['key']=='noise2void' else 'direct_live_text_tool_reads',
            visual_physical_pages_reviewed=[v['physical_page'] for v in visuals],actual_visual_image_files=visuals,
            unread_main_PDF_physical_pages=[9] if p['key']=='noise2void' else [],
            separate_supplementary_acquired=False,separate_supplementary_read=False))
    provenance = dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[entry(handoff),entry(BASE/'portable_extraction_render_attempt01/extraction_render_attempt01.json'),
            entry(ROOT/'literature/2026-10-08_blindspot_dependence_primary_protocol.md'),
            entry(ROOT/'literature/2026-10-08_blindspot_dependence_primary_reading.md')],
        scopes=scopes,new_primary_papers_read=2,related_physical_pages_acquired=20,text_pages_read=19,
        visual_pages_reviewed=5,wrong_identity_physical_pages_acquired=28,
        wrong_identity_page1_only_checked_and_excluded=True,
        wrong_identity_and_related_physical_pages_acquired_total=48,
        noise2void_text_tool_chunks_from_handoff=['0cb6db','df22e4','9df810','abdccc'],
        noise2void_truncated_initial_page1_chunk_excluded='bbd5c4',
        noise2same_direct_text_tool_chunks=['8262a7','9fb1bd','b38d9f'],
        visual_observation_source='five successful direct tools.view_image outputs inspected in two functions.exec batches',
        visual_tool_chunk_identifier_returned=False,
        noise2same_main_body_physical_pages=list(range(1,10)),noise2same_reference_physical_pages=[10,11],
        proof_appendices_A_B_not_in_main_PDF_and_not_read=True,AuthorFeedback_not_acquired=True,
        acquisition_and_render_receipts_not_rewritten=True,author_training_reproduced=False,
        extra_reference18_paper_identified_only_not_acquired_or_read=True,
        pypdf_extraction_warnings=['Ignoring wrong pointing object 98 0 (offset 0)',
            'Ignoring wrong pointing object 125 0 (offset 0)'])
    provenance_path = ROOT/'literature/blindspot_dependence_reading_provenance_2026-10-08.json'
    new(provenance_path,provenance)
    roots = []
    for name,digest in (('.gitignore','7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524'),
                        ('environment.yml','dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257')):
        p = ROOT.parent/name
        assert sha(p)==digest
        roots.append(dict(path=str(p),sha256=digest,previous_sha256=digest,unchanged=True))
    observations = dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],actual_exits=exits,
        imported_training_polls=[dict(chunk='04bb16',session=99542,new_output=False),
            dict(chunk='bc884b',session=99542,native_updates=16236),
            dict(chunk='a03adf',session=99542,native_updates=16533,new_updates=16434,cumulative_wall_seconds=37476.97783989995)],
        direct_training_polls=[dict(chunk='94708a',session=99542,native_updates=16929,new_updates=16830,cumulative_wall_seconds=38399.800927300006),
            dict(chunk='9bb92a',session=99542,native_updates=17028,new_updates=16929,cumulative_wall_seconds=38635.90585660003),
            dict(chunk='5b0c00',session=99542,native_updates=17325,new_updates=17226,cumulative_wall_seconds=39343.26285689999)],
        training_handle_still_live=True,full_training_observed_tool_exit=None,
        latest_GPU=dict(actual_observed_tool_chunk='5c8521',actual_observed_tool_exit=0,timestamp='2026/10/08 02:30:11.657',
            free_MiB=1394,total_MiB=24455,utilization_percent=92,new_GPU8GB_margin_met=False),
        retained_metadata_or_environment_failures=[
            dict(chunk='8a426e',exit=1,kind='rg encountered pre-existing inaccessible pip temp dirs; no edits'),
            dict(chunk='0c663c',exit=1,kind='rg no AGENTS.md matches in .agents/.codex; no applicable files found'),
            dict(chunk='b9de2e',exit=1,kind='PowerShell native rg regex quoting parse error'),
            dict(chunk='37c028',overall_command_exit=0,subcommand='rg missing guessed MC_RC_FULL_REFERENCE_PROTOCOL filename'),
            dict(chunk='a1d4b6',exit=1,kind='metadata summary used production key on independent receipt; no outputs or arrays'),
            dict(chunk='99c2d8',exit=-1073740791,source='imported_handoff',kind='MiKTeX AppData log failure; PDF 11 pages printed'),
            dict(chunk='e20b37',exit=-1073740791,source='imported_handoff',kind='MIKTEX_LOG_DIR did not redirect existing tool')],
        new_version_summary_correction=dict(v1='experiments/summarize_observed_holdout_feature_2026_10_08.py',
            v2='experiments/summarize_observed_holdout_feature_v2_2026_10_08.py',
            source_data_changed=False,independent_receipt_counter_names_used=True),
        permitted_escalated_public_GET_reader_v3_actual_tool_chunk='62ac3c',
        automatic_approval_review_rejections_received=0,TLS_certificate_verification_disabled=False,
        MRI_environment_modified=False,pip_invoked=False,other_processes_enumerated=False,
        user_terminal_processes_controlled=False,training_restarted=False,training_migrated=False,new_agents_delegated=False,
        used_skill='pdf:pdf',skill_path='C:/Users/user/.codex/plugins/cache/openai-primary-runtime/pdf/26.904.11930/skills/pdf/SKILL.md',
        skill_use_was_read_only_no_PDF_authoring=True)
    obs = ROOT/'SESSION_TOOL_OBSERVATIONS_OBSERVED_HOLDOUT_2026-10-08.json'
    new(obs,observations)
    ledger = dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[entry(Path(__file__)),entry(handoff),entry(obs),entry(provenance_path),
            entry(ROOT/'experiments/observed_holdout_feature_table_2026_10_08.json')]+[entry(ROOT/path) for key,path,chunk,code in imported+direct],
        actual_exits=exits,root_files_observed=roots,
        unique_development_patients=11,unique_development_series=19,observed_package_load_events=41,
        production_observed_load_events=19,failed_independent_observed_load_events=3,v2_independent_observed_load_events=19,
        unique_real_folds=38,counterfactual_check_events=81,original_independent_failed=True,failed_attempt_retained=True,
        layout_v2_passed=True,no_tolerance_widening=True,
        neural_forwards=0,GPU_forwards=0,training_updates=0,model_arrays_loaded=0,
        metadata_summary_and_export_new_medical_array_loads=0,
        counts_exclude_original_live_training_and_hash_byte_IO=True,
        feature_rows=19,feature_names=17,real_action_utility_labels_available=False,
        new_primary_papers_read=2,related_physical_pages_acquired=20,text_pages_read=19,visual_pages_reviewed=5,
        wrong_identity_paper_excluded=True,separate_supplementary_not_acquired_or_read=True,
        latest_training_poll=observations['direct_training_polls'][-1],latest_GPU=observations['latest_GPU'],
        original_training_session=99542,full_training_observed_tool_exit=None,
        formal_final_budget_completed=False,original56FOV_evaluated=False,all6_final_capability_gates_completed=False,
        actual_MRI_task_benefit_measured=False,real_task_latency_measured=False,actual_MRI_risk_certificates_issued=0,
        native_GT_validation_confirmation_pixels_read=False,confirmation_patients_opened=False,
        validation_data_read=False,locked_IXI_opened=False,old_MIRA_MSValid84_confirmation_preserved=True,
        publication_claim_confirmed=False,goal_status='active',current_goal_turn_classification='progress',
        stage_max_saved_bytes=50_000_000,medical_job_saved_limit_remains=20_000_000)
    new(ROOT/'SESSION_EXECUTION_LEDGER_OBSERVED_HOLDOUT_2026-10-08.json',ledger)
    print(json.dumps(dict(complete=True,observed_package_load_events=41,unique_folds=38,
        counterfactual_check_events=81,feature_rows=19,features=17,text_pages_read=19,visual_pages_reviewed=5,
        native_updates=17325,full_training_exit=None,goal_status='active',publication_claim_confirmed=False)),flush=True)
    return 0


if __name__=='__main__':
    raise SystemExit(main())
