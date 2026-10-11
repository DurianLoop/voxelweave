"""Bind actual observed exits, reading scope, medical counts and root hashes."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),bytes=p.stat().st_size)
def new(p,v):
    with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    actual=[
        ('dependency_install_v1','tools/anchor_forest_runtime_2026_10_07/install_attempt01.json','405648',1,'user_provided_handoff'),
        ('dependency_install_v2','tools/anchor_forest_runtime_v2_2026_10_07/install_attempt02.json','c77a29',1,'user_provided_handoff'),
        ('dependency_install_v3','tools/anchor_forest_runtime_v3_2026_10_07/install_attempt03.json','1e0bc7',1,'user_provided_handoff'),
        ('joblib_public_TLS12','tools/anchor_forest_joblib_tls12_2026_10_07/acquisition_attempt01.json','d16896',0,'user_provided_handoff'),
        ('dependency_install_v4','tools/anchor_forest_runtime_v4_2026_10_07/install_attempt04.json','c8677b',0,'user_provided_handoff'),
        ('diagnostic_v1','experiments/mc_rc_anchor_prior_forest_diagnostic_2026_10_07/attempt01.json','8a9599',1,'user_provided_handoff'),
        ('diagnostic_v2','experiments/mc_rc_anchor_prior_forest_diagnostic_v2_2026_10_07/attempt01.json','1585da',1,'user_provided_handoff'),
        ('diagnostic_v3','experiments/mc_rc_anchor_prior_forest_diagnostic_v3_2026_10_07/attempt01.json','202730',1,'live_tool_result'),
        ('diagnostic_v4','experiments/mc_rc_anchor_prior_forest_diagnostic_v4_2026_10_07/attempt01.json','c31426',0,'live_tool_result'),
        ('independent_diagnostic','experiments/mc_rc_anchor_prior_forest_diagnostic_v4_2026_10_07/independent_label_models_roi_attempt01.json','779eda',0,'live_tool_result'),
        ('metadata_amortization','experiments/mc_rc_anchor_prior_forest_amortization_2026_10_07/attempt01.json','fe2e70',0,'live_tool_result'),
        ('primary_acquisition_attempt01','literature/source_cache/prior_balance_primary_2026-10-07/acquisition_attempt01.json','e4b57d',1,'live_tool_result'),
        ('arxiv_acquisition_attempt02','literature/source_cache/prior_balance_primary_attempt02_2026-10-07/acquisition_attempt01.json','dfb178',0,'live_tool_result'),
        ('primary_render','literature/source_cache/prior_balance_visual_2026-10-07/render_attempt01.json','847b6e',0,'live_tool_result')]
    exits=[dict(key=k,**entry(ROOT/p),actual_observed_tool_chunk=c,actual_observed_tool_exit=e,exit_observation_source=s) for k,p,c,e,s in actual]
    v1=read(ROOT/actual[5][1]);v2=read(ROOT/actual[6][1]);v3=read(ROOT/actual[7][1]);prod=read(ROOT/actual[8][1]);verify=read(ROOT/actual[9][1]);cost=read(ROOT/actual[10][1])
    assert not v1['complete'] and v1['forest_models_fitted']==0 and len(v1['series_statistics'])==19 and v1['full_development_GT_arrays_loaded']==0
    assert v1['errors'][0].startswith('PermissionError: [WinError 5] ') and '_winapi.CreateFile' in v1['traceback']
    assert not v2['complete'] and v2['errors']==['AssertionError: '] and '?????' in v2['traceback']
    assert not v3['complete'] and v3['prohibited_access_attempts']==[str(ROOT/'experiments/mc_rc_anchor_prior_forest_diagnostic_2026_10_07.py')]
    assert all(d['complete'] and not d['errors'] and not d.get('prohibited_access_attempts',[]) for d in (prod,verify,cost))
    assert prod['all19_predictions_saved_before_full_GT_scoring'] and len(prod['series'])==len(prod['prediction_receipts'])==19 and len(prod['folds'])==11
    assert verify['checked_series']==19 and verify['checked_candidate_supports']==57 and verify['checked_missing_plane_records']==3015 and verify['forest_trees_compared']==704
    assert verify['forest_models_refitted']==11 and verify['QDA_models_rederived']==22 and verify['fresh_anchor_classifier_calls']==1062
    for doc in (v1,prod,verify,cost):
        for binding in doc['source_bindings']:assert sha(ROOT/binding['path'])==binding['sha256'],binding['path']
        for snap in doc.get('source_snapshots',[]):assert sha(ROOT/snap['snapshot']['path'])==snap['snapshot']['sha256']==sha(ROOT/snap['source_path'])
    install=read(ROOT/actual[4][1]);assert install['complete'] and not install['errors'] and not install['existing_environment_modified']
    for f in install['installed_files']:assert sha(ROOT/f['path'])==f['sha256']
    for f in install['acquisitions']:assert sha(ROOT/f['wheel_file'])==f['wheel_sha256']==f['official_sha256']
    for method in cost['models']:
        summary=next(x for x in prod['summaries'] if x['method']==method['method'])
        assert summary['full_forward_calls_total']==method['N_total'] and summary['recomputed_batch_pairs_total']==method['k_total'] and summary['ROI_gates_passed']==method['all_gates_pass']==0
        assert abs(method['legacy_patient_series_equal_ratios']['5']['value']-(1.2-summary['patient_first_means']['saved_forward_fraction']))<1e-12
    acquisitions=[read(ROOT/actual[11][1]),read(ROOT/actual[12][1])]
    first=acquisitions[0]['records'];assert not first[0]['complete'] and first[0]['errors']==['HTTPError: HTTP Error 403: Forbidden'] and first[1]['complete']
    logit=acquisitions[1]['records'][0];cb=first[1];assert logit['complete'] and logit['physical_pages']==27 and cb['physical_pages']==10
    images=read(ROOT/actual[13][1])['records'];assert len(images)==4
    scopes=[]
    for paper,pages in [(logit,list(range(1,12))+[17,18]),(cb,list(range(1,9)))]:
        texts=[p for p in paper['page_texts'] if p['physical_page'] in pages]
        visuals=[p for p in images if p['key']==paper['key']]
        for b in [paper['PDF']]+texts+visuals:assert sha(ROOT/b['path'])==b['sha256']
        scopes.append(dict(key=paper['key'],PDF=paper['PDF'],physical_pages_text_read=pages,page_texts=texts,actual_visual_image_files=visuals,visual_reviewed_pages=[p['physical_page'] for p in visuals],unread_physical_pages=[p for p in range(1,paper['physical_pages']+1) if p not in pages]))
    provenance=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],new_primary_papers_read=2,text_pages_read=21,physical_pages_visual_reviewed=4,source_bindings=[entry(ROOT/actual[i][1]) for i in (11,12,13)],scopes=scopes,
        actual_visual_tool='functions.exec -> four tools.view_image with returned images',author_training_reproduced=False,all_supplementary_pages_read=False)
    literature=ROOT/'literature/prior_balance_reading_provenance_2026-10-07.json';new(literature,provenance)
    observed=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],actual_exits=exits,
        resumed_training_polls=[dict(tool_chunk='81cf5b',session_id=99542,native_updates=12276,new_updates=12177,cumulative_wall_seconds=27481.999204199994),dict(tool_chunk='5539e0',session_id=99542,native_updates=12474,new_updates=12375,cumulative_wall_seconds=27946.634527900023),dict(tool_chunk='fa8646',session_id=99542,native_updates=12573,new_updates=12474,cumulative_wall_seconds=28176.22950170003),dict(tool_chunk='eca1bc',session_id=99542,native_updates=12870,new_updates=12771,cumulative_wall_seconds=28846.14151320001)],
        full_training_observed_tool_exit=None,training_restarted=False,training_migrated=False,user_terminal_processes_controlled=False,
        GPU=dict(actual_observed_tool_chunk='3a79c6',actual_observed_tool_exit=0,timestamp='2026/10/07 23:48:48.906',free_MiB=1394,total_MiB=24455,utilization_percent=85,new_GPU8GB_margin_met=False),
        reversible_source_creation_tools=[dict(tool_chunk='7b36c0',exit_code=0,version='v3'),dict(tool_chunk='7646c1',exit_code=0,version='v4'),dict(tool_chunk='4670af',exit_code=0,version='arxiv_fetch_attempt02')],
        non_scientific_query_issues=[dict(tool_chunk='ff5adc',exit_code=1,reason='rg encountered old inaccessible pip temp directories; no mutation'),dict(tool_chunk='32f23d',exit_code=0,contained_rg_exit_failure=True,reason='Windows literal wildcard path error123; corrected glob search9c1325'),dict(tool_chunk='be920a',exit_code=1,reason='optional read used download_attempt01.json instead of existing acquisition_attempt01.json; subsequent metadata reads actual existing receipt')],
        automatic_approval_review_rejections_received=0)
    obsfile=ROOT/'SESSION_TOOL_OBSERVATIONS_ANCHOR_PRIOR_2026-10-07.json';new(obsfile,observed)
    root_observed=[]
    for row in read(ROOT/'SESSION_EXECUTION_LEDGER_OBSERVED_ROI_2026-10-07.json')['root_files_observed']:
        h=sha(Path(row['path']));assert h==row['sha256'];root_observed.append(dict(path=row['path'],sha256=h,previous_sha256=row['sha256'],unchanged=True))
    counts={key:sum(d.get(key,0) for d in (v1,v2,v3,prod,verify)) for key in ('observed_MRI_packages_loaded','observed_label_arrays_loaded','full_development_GT_arrays_loaded')}
    assert counts==dict(observed_MRI_packages_loaded=76,observed_label_arrays_loaded=38,full_development_GT_arrays_loaded=38)
    ledger=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],source_bindings=[entry(Path(__file__)),entry(obsfile),entry(literature)]+[entry(ROOT/actual[i][1]) for i in range(11)],actual_exits=exits,
        unique_development_patients=11,unique_development_series=19,checked_supports=57,checked_missing_plane_records=3015,forest_trees_compared=704,independent_QDA_rederived=22,
        actual_medical_array_counts_including_failed_preparation=counts,production_forest_models=11,independent_forest_refits=11,
        production_anchor_classifier_calls=prod['anchor_classifier_calls'],independent_anchor_classifier_calls=1062,
        new_native_reference_MRI_arrays_loaded=0,new_neural_forwards=0,new_GPU_forwards=0,new_neural_training_updates=0,medical_array_count_excludes_live_original_training=True,
        actual_MRI_risk_certificates_issued=0,clinical_benefit_measured=False,real_latency_measured=False,publication_claim_confirmed=False,confirmation_patients_opened=False,validation_data_read=False,old_MIRA_MSValid84_confirmation_preserved=True,
        all_primary_ROI_gates_passed_series=0,primary_method='joint_QDA_balanced_prior_19',primary_coverage_and_positive_conditional_saving_series=12,
        new_primary_papers_read=2,text_pages_read=21,visual_pages_reviewed=4,root_files_observed=root_observed,
        live_training_session=99542,latest_training_poll=observed['resumed_training_polls'][-1],full_training_observed_tool_exit=None,new_GPU8GB_margin_met=False,
        failures_preserved=True,scientific_settings_not_tuned_after_scoring=True,goal_status='active',current_goal_turn_classification='progress')
    new(ROOT/'SESSION_EXECUTION_LEDGER_ANCHOR_PRIOR_2026-10-07.json',ledger)
    print(json.dumps(dict(complete=True,checked_series=19,checked_supports=57,forest_trees_compared=704,array_counts=counts,new_primary_papers_read=2,text_pages_read=21,visual_pages_reviewed=4,root_hashes_unchanged=True,goal_status='active',publication_claim_confirmed=False)),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
