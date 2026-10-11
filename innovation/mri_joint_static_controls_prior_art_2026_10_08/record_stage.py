"""Bind observed exits, exact reading range and remaining real experimental gaps."""
import json,sys,time,hashlib,subprocess,shutil
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;PROJECT=ROOT.parent
sys.path.insert(0,str(ROOT/'task_adaptation_compute_prior_art_2026_10_08'))
import query_primary as base
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
    sys.stdout.reconfigure(encoding='utf-8');base.own_priority();tick=time.perf_counter()
    primary=read(HERE/'primary_attempt01/receipt.json');retry=read(HERE/'thesis_size_verified_attempt02/receipt.json')
    thesis=read(HERE/'thesis_text_attempt01/receipt.json');visual=read(HERE/'visual_attempt01/receipt.json')
    audit=read(HERE/'table_audit_attempt01/receipt.json');gen=read(HERE/'ARCHIVE_ENTRY_GENERATION.json')
    assert not primary['complete'] and primary['records'][0]['complete'] and primary['records'][1]['curl_exit']==63
    assert not retry['complete'] and retry['curl_exit']==0 and len(retry['errors'])==1
    assert thesis['complete'] and thesis['local_source_version_identity_passed'] and not thesis['ETag_sha256_match']
    for d in (thesis,visual,audit,gen):assert d['complete'] and not d['errors']
    records=[]
    jobs=[('masc',primary['records'][0],list(range(1,13))+[17,18,19],[],[4,5,7,10,11,12,17,18]),
        ('thesis',thesis,list(range(60,67))+list(range(94,97))+list(range(102,116)),[1,7,8,9,10],[66,110,112,114])]
    for key,data,mainpages,front,images in jobs:
        bypage={p['physical_page']:p for p in data['page_texts']};pages=sorted(mainpages+front)
        for n in pages:
            b=bypage[n];actual=base.entry(ROOT/b['path']);assert actual['sha256']==b['sha256'] and actual['bytes']==b['bytes']
        rendered=[r for r in visual['records'] if r['paper']==key]
        assert sorted(r['physical_page'] for r in rendered)==sorted(images)
        records.append(dict(key=key,original_PDF=data['file'],physical_pages=data['physical_pages'],
            full_text_pages_read=pages,main_text_pages_read=mainpages,main_text_page_count=len(mainpages),
            ancillary_frontmatter_pages_read=front,full_text_page_count=len(pages),
            visual_pages_reviewed=images,visual_page_count=len(images),
            full_text_page_bindings=[bypage[n] for n in pages],visual_page_bindings=rendered,
            pages_not_read_in_full=[n for n in range(1,data['physical_pages']+1) if n not in pages],
            code_repository_or_implementation_read=False,raw_patient_results_obtained=False,
            experimental_results_independently_reproduced=False,
            expected_ETag_sha256_verified=False if key=='thesis' else None))
    assert sum(r['main_text_page_count'] for r in records)==39
    assert sum(r['full_text_page_count'] for r in records)==44
    provenance=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],records=records,
        source_bindings=[base.entry(HERE/p) for p in ('PRIMARY_READING.md','primary_attempt01/receipt.json',
            'thesis_text_attempt01/receipt.json','visual_attempt01/receipt.json','THESIS_BODY_IDENTITY_CLARIFICATION.md')],
        new_primary_papers_read=2,new_primary_sources_read=2,source_types=['research_paper','doctoral_thesis_selected_chapters'],
        new_full_text_pages_read=44,main_text_pages_read=39,ancillary_frontmatter_pages_read=5,visual_pages_reviewed=12,
        thesis_not_read_in_entirety=True,thesis_secondary_openreview_article_not_downloaded=True,
        extraction_and_render_receipt_false_flags_are_generation_snapshots=True,
        original_failed_receipts_preserved=True,full_systematic_novelty_search_completed=False,
        medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0)
    base.new(HERE/'READING_PROVENANCE.json',provenance)
    assert len(audit['metric_specific_static_comparisons'])==15
    assert len(audit['thesis_endpoint_aggregation_comparisons'])==4
    reversal=audit['thesis_endpoint_aggregation_comparisons'][3]
    assert reversal['strict_sign_reversal'] and reversal['RL_minus_LBCS_final_SSIM']=='-0.0006'
    assert reversal['RL_minus_LBCS_SSIM_AUC']=='0.0015'
    sources=[HERE/p for p in ('primary_attempt01/receipt.json','static_index_attempt01/receipt.json',
        'thesis_size_verified_attempt02/receipt.json','thesis_identity_attempt01/receipt.json','thesis_text_attempt01/receipt.json',
        'visual_attempt01/receipt.json','table_audit_attempt01/receipt.json','ARCHIVE_ENTRY_GENERATION.json','READING_PROVENANCE.json')]
    bindings=[]
    for source in sources:
        d=read(source)
        for b in d.get('source_bindings',[])+d.get('output_bindings',[]):
            actual=base.entry(ROOT/b['path']);assert actual['sha256']==b['sha256']
            if 'bytes' in b:assert actual['bytes']==b['bytes']
            bindings.append(dict(document=source.relative_to(ROOT).as_posix(),**b))
    roots=[]
    for name,expected in [('.gitignore','7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524'),
        ('environment.yml','dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257')]:
        p=PROJECT/name;assert hashlib.sha256(p.read_bytes()).hexdigest()==expected
        roots.append(dict(path=str(p),sha256=expected,previous_sha256=expected))
    gpu=subprocess.run(['nvidia-smi','--query-gpu=timestamp,name,memory.total,memory.free,utilization.gpu','--format=csv,noheader'],
        capture_output=True,text=True,timeout=15);assert gpu.returncode==0
    csv=gpu.stdout.strip();freeMiB=int(csv.split(',')[3].strip().split()[0]);freebytes=freeMiB*1048576
    livepath=ROOT/'experiments/mc_rc_3d_19series_common_init_cpu_2026_10_07/invocation02.json'
    raw=livepath.read_bytes();live=json.loads(raw)
    obs=dict(observed_utc=datetime.now(timezone.utc).isoformat(),training_session_id=99542,original_training_terminal_exit=None,
        training_status=live.get('status'),training_complete=live.get('complete'),training_errors=live.get('errors'),
        arms=[{k:a.get(k) for k in ('kind','updates_completed','complete')} for a in live.get('arms',[])],
        invocation02_new_updates=live.get('new_cpu_backbone_updates'),new_updates_not_raw_arm_count=True,
        live_metadata_SHA256_observation_not_frozen=hashlib.sha256(raw).hexdigest(),mutable_training_file_not_added_to_archive=True,
        gpu_csv=csv,gpu_query_exit=0,gpu_free_bytes=freebytes,gpu_authorization_retained=True,new_GPU_job_started=False,
        new_GPU_startup_reserve_bytes=8_000_000_000,GPU_reserve_met=freebytes>=8_000_000_000,
        workspace_free_bytes=shutil.disk_usage(ROOT).free,disk_reserve_bytes=8_000_000_000,root_files_observed=roots,
        original_terminal_training_modified=False,other_processes_enumerated=False,other_processes_modified=False)
    base.new(HERE/'TRAINING_RESOURCE_OBSERVATION.json',obs)
    ledger=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[base.entry(Path(__file__))]+[base.entry(p) for p in sources]+[base.entry(HERE/p) for p in
            ('PROTOCOL.md','RESULT.md','MATCHED_STATIC_ADAPTATION_PREPARATION.md','USER_GOAL_REQUEST.md','VISIBLE_DIALOGUE.md',
            'NEXT_STAGE_HANDOFF.md','DELIVERY.md','TRAINING_RESOURCE_OBSERVATION.json')],
        source_bindings_verified=bindings,all_source_bindings_verified=True,source_originals_not_overwritten=True,
        actual_exits=[dict(chunk='5827e6',exit_code=1,job='first_bounded_public_fetch',MASC_succeeded=True,thesis_CURL_exit=63),
            dict(chunk='d97fb8',exit_code=0,job='static_article_index_query',returned_rows=2,unique_papers=1,new_unique_papers=0),
            dict(chunk='aa837c',exit_code=1,job='size_verified_download_attempt02',HTTP_status=200,CURL_exit=0,
                complete_length_passed=True,ETag_SHA_match=False),
            dict(chunk='c94193',exit_code=0,job='actual_local_PDF_SHA256_observation'),
            dict(chunk='444c08',exit_code=0,job='local_thesis_identity_inspection'),
            dict(chunk='662022',exit_code=0,job='qualified_local_thesis_text_extraction'),
            dict(chunk='5bf945',exit_code=0,job='render_12_source_pages'),
            dict(chunk='792814',exit_code=0,job='CPU_reported_table_arithmetic_audit')],
        known_executed_failures_preserved=True,download_failure_does_not_equal_automatic_approval_rejection=True,
        original_live_polls=[dict(chunk='acda01',session_id=99542,returned_session_id=99542,terminal_exit=None,
            raw_pchip_updates=1980,loss=1.1260886192321777,invocation02_new_updates=21780,cumulative_wall_seconds=50115.28277489997),
            dict(chunk='026b5c',session_id=99542,returned_session_id=99542,terminal_exit=None,
                raw_pchip_updates=2079,loss=1.1138702630996704,invocation02_new_updates=21879,cumulative_wall_seconds=50351.026271399925)],
        index_abstracts_screened=2,index_unique_papers=1,new_index_unique_papers=0,
        new_primary_papers_read=2,new_primary_sources_read=2,new_full_text_pages_read=44,
        main_text_pages_read=39,ancillary_frontmatter_pages_read=5,visual_pages_reviewed=12,
        metric_specific_static_table_comparisons=15,thesis_endpoint_summary_comparisons=4,
        thesis_DDQN_metric_differences=12,MASC_frozen_metric_differences=5,
        CPU_arithmetic_only=True,summary_comparisons_not_independent_patient_records=True,
        medical_arrays_loaded=0,model_checkpoint_arrays_loaded_from_disk=0,neural_forwards=0,MRI_neural_forwards=0,GPU_forwards=0,
        real_medical_resource_updates=0,real_medical_formal_training_updates=0,head_fits=0,new_final_action_labels_generated=0,
        full_action_cost_measured=False,actual_new_MRI_task_benefit_measured=False,original56FOV_evaluation_launched=False,
        formal_three_arm_training_implemented_and_qualified=False,confirmation_patients_opened=False,lockedIXI_opened=False,
        original_terminal_training_modified=False,new_agents_delegated=0,automatic_approval_review_rejections_received=0,
        root_files_observed=roots,publication_claim_confirmed=False,goal_status='active',
        previous_goal_turn_classification='progress',current_goal_turn_classification='progress',
        current_progress='Read MRI co-adaptation and static-control sources; audited metric-specific strongest static baselines and strict aggregation ranking reversal; prepared matched adaptation and static counterfactual controls.',
        completion_audit=dict(original_two_arm_final_not_complete=True,original_task_capability_not_yet_evaluated=True,
            strong_matched_three_arm_task_effects_not_measured=True,full_action_cost_unknown=True,
            novel_MRI_effect_not_confirmed=True,eight_unseen_patient_confirmation_not_opened=True),
        original_live_terminal_exit_not_inferred_from_metadata=True,
        ancillary_read_failure='Broad thesis rg output was truncated; only subsequent complete-page outputs counted.',
        elapsed_seconds=time.perf_counter()-tick)
    base.new(HERE/'EXECUTION_LEDGER.json',ledger)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<30_000_000
    print(json.dumps(dict(complete=True,new_primary_sources=2,main_text_pages=39,ancillary_frontmatter_pages=5,
        total_full_text_pages=44,visual_pages=12,neural_forwards=0,gpu_free_bytes=freebytes,
        workspace_free_bytes=obs['workspace_free_bytes'],root_hashes_unchanged=True,goal_status='active'),ensure_ascii=False),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
