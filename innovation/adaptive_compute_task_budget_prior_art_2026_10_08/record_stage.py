"""Bind final reading and research preparation to actual recorded executions."""
import sys,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'seranet_identity_prior_art_2026_10_08'))
import query_seranet_stdlib_v3 as client
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    sys.stdout.reconfigure(encoding='utf-8');resources=client.resource_guard()
    obs=read(HERE/'ACTUAL_OBSERVATIONS.json');primary=read(HERE/'primary_attempt01/receipt.json')
    visual=read(HERE/'visual_attempt01/receipt.json');index=read(HERE/'index_attempt01/receipt.json')
    author=read(HERE/'author_index_attempt01/receipt.json');audit=read(HERE/'cpu_audit_attempt01/receipt.json')
    for q in (obs,primary,visual,index,author,audit):assert q['complete'] and not q['errors']
    assert sum(len(r['entries']) for r in index['records'])==18
    assert len({e['id'] for r in index['records'] for e in r['entries']})==18
    assert sum(len(r['entries']) for r in author['records'])==9
    papers=[]
    for r in primary['records']:
        key=r['key'];textobs=[o for o in obs['current_tool_observations'] if o.get('complete_text_read',{}).get('paper')==key]
        pages=[n for o in textobs for n in o['complete_text_read']['physical_pages']]
        assert sorted(pages)==list(range(1,r['physical_pages']+1)) and len(set(pages))==len(pages)
        visualpages=[n for o in obs['actual_visual_reviews'] if o['paper']==key for n in o['physical_pages']]
        images=[v for v in visual['records'] if v['key']==key]
        assert set(visualpages)=={v['physical_page'] for v in images} and len(visualpages)==len(set(visualpages))
        papers.append(dict(key=key,indexed_identity=r['indexed_record'],PDF_source=r['file'],
            text_pages_read=[dict(**b,actual_text_read=True,actual_read_chunk=next(o['chunk_id'] for o in textobs if b['physical_page'] in o['complete_text_read']['physical_pages'])) for b in r['page_texts']],
            visual_pages_reviewed=[dict(**v,actual_visual_reviewed=True) for v in images],
            full_text_pages_read=len(pages),different_visual_pages_reviewed=len(images),
            author_code_reproduced=False,medical_task_effect_verified_here=False))
    counts=obs['counts'];assert [sum(p['full_text_pages_read'] for p in papers),sum(p['different_visual_pages_reviewed'] for p in papers)]==[32,19]
    assert audit['rows_checked']==39 and audit['all39_transcribed_rows_match_actual_extracted_text']
    docs=[Path(__file__),HERE/'PROTOCOL.md',HERE/'PRIMARY_SELECTION.md',HERE/'PRIMARY_READING.md',HERE/'CPU_EXPLORATION_PLAN.md',
        HERE/'ACTION_VALUE_AND_ACTUAL_COMPUTE_CONTROLS.md',HERE/'ACTUAL_OBSERVATIONS.json',HERE/'RESULT.md',HERE/'VISIBLE_DIALOGUE.md',HERE/'USER_PROVIDED_HANDOFF.md',
        HERE/'index_attempt01/receipt.json',HERE/'primary_attempt01/receipt.json',HERE/'visual_attempt01/receipt.json',
        HERE/'author_index_attempt01/receipt.json',HERE/'cpu_audit_attempt01/receipt.json']
    reading=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],**counts,papers=papers,
        source_bindings=[client.base.entry(p) for p in docs],author_repository_metadata_returned_and_screened=9,
        author_READMEs_read=0,author_source_files_read=0,author_code_reproduced=False,
        original_extraction_and_render_receipts_not_rewritten=True,scientific_claim_confirmed=False)
    client.base.new(HERE/'READING_PROVENANCE.json',reading)
    roots=[]
    for path,expected in [('D:/MRI/.gitignore','7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524'),
        ('D:/MRI/environment.yml','dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257')]:
        p=Path(path);assert sha(p)==expected;roots.append(dict(path=path,sha256=sha(p),previous_sha256=expected))
    zeros={k:0 for k in ('medical_arrays_loaded','model_checkpoint_arrays_loaded_from_disk','neural_forwards','MRI_neural_forwards','GPU_forwards',
        'real_medical_training_updates','head_fits','new_action_labels_generated','new_agents_delegated')}
    ledger=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],**counts,**zeros,
        source_bindings=[client.base.entry(p) for p in docs+[HERE/'READING_PROVENANCE.json',ROOT/'author_implementation_and_sampling_prior_art_2026_10_08/ARCHIVE_PROOF.json']],
        root_files_observed=roots,resource_snapshot=resources,actual_observations=obs,
        math_counterexamples_and_cost_models_are_not_MRI_evidence=True,author_source_not_authenticated=True,
        original_training_terminal_exit=None,latest_raw_arm_updates=6732,latest_invocation_new_updates=26532,
        original_training_modified=False,current_original_contract=dict(per_arm_updates=19998,total_updates=39996,cumulative_wall_limit_hours=30),
        confirmation_patients_opened=False,lockedIXI_opened=False,publication_claim_confirmed=False,goal_status='active',
        previous_frozen_evidence_files_expected=5191,automatic_approval_review_rejections_received=0,
        new_GPU_job_started=False,GPU_user_authorization_present=True)
    client.base.new(HERE/'EXECUTION_LEDGER.json',ledger)
    print(json.dumps(dict(complete=True,**counts,resource_snapshot=resources,goal_status='active',publication_claim_confirmed=False)),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
