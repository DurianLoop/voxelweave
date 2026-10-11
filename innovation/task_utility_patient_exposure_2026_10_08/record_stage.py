"""Register actual reads, tool exits, scope and public delivery without editing prior evidence."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent

def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def new(p,v):
    with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    raw=read(HERE/'primary_attempt01/receipt.json');render=read(HERE/'visual_attempt01/receipt.json')
    registry=read(HERE/'patient_registry_attempt03/receipt.json');verify=read(HERE/'patient_registry_independent_attempt01/receipt.json')
    assert all(v['complete'] for v in (raw,render,registry,verify))
    selected={'dynamicdps':list(range(1,12)),'tackle':list(range(1,13))+list(range(15,20))}
    visuals={'dynamicdps':[4,7,8],'tackle':[7,11,15]};records=[]
    for paper in raw['records']:
        key=paper['key'];p=ROOT/paper['file']['path'];assert entry(p)==paper['file']
        texts=[v for v in paper['page_texts'] if v['physical_page'] in selected[key]]
        imgs=[v for v in render['records'] if v['paper']==key and v['physical_page'] in visuals[key]]
        assert len(texts)==len(selected[key]) and len(imgs)==3
        records.append(dict(key=key,title=paper['indexed_record']['title'],arxiv_version=paper['indexed_record']['id'].rsplit('/',1)[-1],
            pdf=entry(p),complete_text_pages_read=selected[key],visual_pages_actually_reviewed=visuals[key],
            text_files=[{k:v[k] for k in ('path','bytes','sha256')} for v in texts],
            reviewed_images=[v['image'] for v in imgs],original_read_false_receipts_preserved=True,
            excluded_pages_from_full_text_count=[13,14] if key=='tackle' else [],
            excluded_page_reason='Reference pages only partially retrieved in a truncated combined output' if key=='tackle' else None,
            author_code_run=False,author_results_reproduced=False))
    provenance=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],records=records,
        new_independent_primary_papers_read=2,new_full_text_pages_read=28,visual_pages_reviewed=6,
        standalone_supplemental_files_read=0,embedded_TACKLE_supplement_selected_pages_read=[15,16,17,18,19],
        index_results_not_systematic_review=True,
        source_bindings=[entry(p) for p in (Path(__file__),HERE/'PRIMARY_READING.md',HERE/'primary_attempt01/receipt.json',HERE/'visual_attempt01/receipt.json')])
    new(HERE/'READING_PROVENANCE.json',provenance)
    tool_exits=[dict(tool_chunk='6b5266',action='initial_public_indices',exit_code=0),
        dict(tool_chunk='7abff2',action='followup_public_indices',exit_code=0),
        dict(tool_chunk='a19b44',action='selected_two_PDFs_and_extraction_terminal',session_id=34470,exit_code=0),
        dict(tool_chunk='39d1ea',action='registry_v1',exit_code=1),
        dict(tool_chunk='52f33d',action='registry_v2',exit_code=1),
        dict(tool_chunk='96d8d7',action='registry_v3',exit_code=0),
        dict(tool_chunk='abddf2',action='independent_registry_verifier',exit_code=0),
        dict(tool_chunk='e9a23b',action='read_only_PDF_rendering',exit_code=0),
        dict(tool_chunk='cef344',action='PowerShell_inline_python_quote_failure_before_index_read',exit_code=1),
        dict(tool_chunk='477a46',action='GPU_and_disk_readonly_snapshot',exit_code=0)]
    live=dict(tool_chunk='df65e5',session_id=99542,still_live=True,observed_terminal_exit=None,
        native_updates=19602,invocation02_native_new_updates=19503,cumulative_wall_seconds=44692.00497759995,
        raw_pchip_last_observation_is_historical=True,final_training_success_claimed=False,
        original_training_restarted=False,user_terminal_process_controlled=False)
    roots=[]
    expect={'.gitignore':'7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524',
            'environment.yml':'dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257'}
    for name,digest in expect.items():
        p=ROOT.parent/name;actual=hashlib.sha256(p.read_bytes()).hexdigest();assert actual==digest
        roots.append(dict(path=str(p),sha256=actual,previous_sha256=digest))
    ledger=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],actual_observed_tool_exits=tool_exits,
        original_live_training=live,
        GPU_snapshot=dict(tool_chunk='477a46',timestamp_local='2026/10/08 04:14:51.882',free_MiB=1394,total_MiB=24455,utilization_percent=57,
                          new_GPU_job_reserve_satisfied=False,new_GPU_job_started=False),
        disk_free_bytes_observed=8429166592,stage_saved_limit_bytes=30_000_000,
        new_independent_primary_papers_read=2,new_full_text_pages_read=28,visual_pages_reviewed=6,
        medical_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,training_updates=0,head_fits=0,
        actual_task_action_labels_generated=0,head_fold_count=11,unique_development_patients=11,unique_development_series=19,
        head_heldout_patients_seen_by_task_training_config=11,whole_pipeline_patient_out_folds=0,
        metadata_negative_checks_actually_executed=11,independent_metadata_folds_rebuilt=11,
        actual_MRI_task_benefit_measured=False,full_action_cost_measured=False,theoretical_risk_certificate_issued=False,
        final_label_bundle_adapter_qualified=False,baseline_cost_gain_equivalence_already_known=True,
        existing_complete_series_adapter_reused_in_preparation=True,old57600_toy_target_replayed=False,
        automatic_approval_review_rejections_received=0,new_agents_spawned=0,root_files_observed=roots,
        confirmation_patients_opened=False,locked_IXI_opened=False,publication_claim_confirmed=False,goal_status='active',
        source_bindings=[entry(p) for p in (Path(__file__),HERE/'PROTOCOL.md',HERE/'PRIMARY_READING.md',HERE/'MATCHED_HEAD_AND_LABEL_PREPARATION.md',
            HERE/'READING_PROVENANCE.json',HERE/'patient_registry_attempt03/receipt.json',HERE/'patient_registry_independent_attempt01/receipt.json')])
    new(HERE/'EXECUTION_LEDGER.json',ledger)
    print(json.dumps({k:ledger[k] for k in ('complete','new_independent_primary_papers_read','new_full_text_pages_read',
        'visual_pages_reviewed','head_fold_count','whole_pipeline_patient_out_folds','actual_task_action_labels_generated','goal_status')},ensure_ascii=False),flush=True)
    return 0

if __name__=='__main__':raise SystemExit(main())
