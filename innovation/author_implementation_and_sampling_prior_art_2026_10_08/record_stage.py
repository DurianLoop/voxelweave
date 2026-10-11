"""Record actual original reading, bounded search scope and CPU-only evidence."""
import sys,json,hashlib
from datetime import datetime,timezone
from pathlib import Path
import query_author_sources as client
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
def read(p):return json.loads(p.read_text(encoding='utf-8'))

def main():
    sys.stdout.reconfigure(encoding='utf-8');client.base.own_priority();resources=client.previous.resource_guard()
    obs=read(HERE/'ACTUAL_OBSERVATIONS.json');audit=read(HERE/'table_audit_attempt01/receipt.json')
    primary=read(HERE/'primary_attempt01/receipt.json')['records'][0]
    assert primary['complete'] and primary['physical_pages']==9
    assert audit['complete'] and not audit['errors'] and audit['transcribed_rows_checked']==16
    src=HERE/'primary_attempt01/acar.pdf';assert client.base.entry(src)==primary['file']
    sources=[Path(__file__),HERE/'PROTOCOL.md',HERE/'PRIMARY_READING.md',HERE/'FIXED_OBSERVATION_AND_ROI_CONTROLS.md',
        HERE/'ACTUAL_OBSERVATIONS.json',HERE/'table_audit_attempt01/receipt.json',HERE/'index_attempt01/receipt.json',
        HERE/'index_attempt02/receipt.json',HERE/'index_attempt03/receipt.json',HERE/'publisher_xml_attempt01/receipt.json']
    reading=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[client.base.entry(p) for p in sources],
        records=[dict(paper='acar',DOI='10.1007/978-3-031-17247-2_6',actual_edition='MLMIR2022 LNCS13587 pp53-61',
            PDF_binding=client.base.entry(src),physical_pages=9,full_text_pages_actually_read=list(range(1,10)),
            reference_only_pages=[9],main_or_mixed_pages=list(range(1,9)),
            page_text_bindings=[dict(physical_page=n,actually_read=True,**client.base.entry(HERE/'primary_attempt01'/f'acar_page{n:03d}.txt')) for n in range(1,10)],
            actual_text_chunks=['ceb9d2','a4c828','2ddb40'],visual_pages_actually_viewed=list(range(1,9)),
            image_bindings=[dict(physical_page=n,actually_viewed=True,**client.base.entry(HERE/'visual_attempt01'/f'acar_page{n:03d}.png')) for n in range(1,9)],
            author_code_read=False,author_experiments_reproduced=False)],
        new_primary_papers_read=1,new_full_text_pages_read=9,reference_only_pages_read=1,main_or_mixed_pages_read=8,visual_pages_reviewed=8,
        new_unique_paper_abstracts_only_read=1,abstract_only_paper='Xu/Öksüz 2024 DOI10.1016/j.imavis.2024.105200',
        actual_abstract_origin='index_attempt02 xu_itu metadata description; no full-text read',
        GitHub_repo_metadata_records_screened=10,GitHub_repo_query_count=6,GitHub_repo_README_or_code_read=0,
        public_GET_request_count=13,systematic_review=False,medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,
        publication_claim_confirmed=False,goal_status='active')
    client.base.new(HERE/'READING_PROVENANCE.json',reading)
    roots=[]
    for name,expected in [('.gitignore','7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524'),
                         ('environment.yml','dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257')]:
        p=ROOT.parent/name;got=hashlib.sha256(p.read_bytes()).hexdigest();assert got==expected
        roots.append(dict(path=str(p),sha256=got,previous_sha256=expected))
    ledger=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[client.base.entry(p) for p in [*sources,HERE/'READING_PROVENANCE.json',HERE/'RESULT.md',
            HERE/'NEXT_STAGE_HANDOFF.md',HERE/'VISIBLE_DIALOGUE.md',ROOT/'experiments/mc_rc_reference_resources_2026_10_07.py']],
        actual_execution_observations=obs,new_primary_papers_read=1,new_full_text_pages_read=9,visual_pages_reviewed=8,
        reference_only_pages_read=1,new_unique_paper_abstracts_only_read=1,public_GET_request_count=13,
        public_table_arithmetic_complete=True,all_16_printed_rows_match=True,
        author_P_epsilon_epochs_or_implementation_verified=False,Xu_fulltext_read=False,
        resource_snapshot=resources,root_files_observed=roots,original_training_terminal_exit=None,original_training_modified=False,
        original_training_terminated_restarted_or_migrated=False,GPU_authorization_retained=True,new_GPU_job_started=False,
        medical_arrays_loaded=0,model_checkpoint_arrays_loaded_from_disk=0,neural_forwards=0,MRI_neural_forwards=0,GPU_forwards=0,
        real_medical_training_updates=0,head_fits=0,new_action_labels_generated=0,new_agents_delegated=0,
        confirmation_patients_opened=False,lockedIXI_opened=False,actual_new_MRI_task_benefit_measured=False,
        full_action_cost_measured=False,publication_claim_confirmed=False,goal_status='active',
        current_goal_turn_classification='progress',automatic_approval_review_rejections_received=0)
    client.base.new(HERE/'EXECUTION_LEDGER.json',ledger)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<30_000_000
    print(json.dumps(dict(complete=True,new_primary_papers_read=1,text_pages=9,visual_pages=8,public_table_rows_checked=16,
        resource_snapshot=resources,root_hashes_unchanged=True,medical_arrays_loaded=0,goal_status='active')),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
