"""Append actual stage observations and reading provenance without rewriting receipts."""
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
    primary=read(HERE/'primary_attempt01/receipt.json');visual=read(HERE/'visual_attempt01/receipt.json')
    audit=read(HERE/'cpu_audit_attempt01/receipt.json');web=read(HERE/'author_web_attempt01/receipt.json')
    identity=read(HERE/'author_identity_attempt01/receipt.json')
    for q in [primary,visual,audit,web]:assert q['complete'] and not q['errors']
    assert not identity['complete'] and identity['records'][1]['HTTP_status']==403
    assert audit['rows_checked']==52 and audit['Jaccard_exhaustion']['violations']==0
    r=primary['records'][0];assert r['physical_pages']==43 and r['file']['sha256']=='275e37b395014a2a64fb45fc1f40402d6d636d52b8e4d5c3c2a5a6401c6038c1'
    counts=dict(new_primary_papers_read=1,new_full_text_pages_read=43,visual_pages_reviewed=13,public_table_rows_checked=52)
    current=[dict(chunk_id=c,physical_pages=pages) for c,pages in [('cfe86f',[1,2,3]),('5bbe32',[10,11,12]),
        ('487f96',[29,30,31]),('5f50b8',[34,36,38]),('4a9a82',[41,42]),('e4830e',[15,32,35])]]
    inherited=[dict(chunk_id=c,physical_pages=pages,observation_from_user_provided_handoff=True) for c,pages in [
        ('3dbd85',[4,5,6]),('914d31',[7,8,9]),('ac072d',[13,14,16]),('cc5835',[17,18,19]),
        ('911b5a',[20,21,22,23]),('45c8cb',[24,25,26]),('875dfa',[27,28]),('857aa7',[33]),
        ('9b657d',[37]),('4ccb5d',[39,40,43])]]
    mapping={n:dict(actual_read_chunk=o['chunk_id'],inherited_observation=o.get('observation_from_user_provided_handoff',False)) for o in current+inherited for n in o['physical_pages']}
    assert sorted(mapping)==list(range(1,44)) and len(mapping)==43
    obs=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],counts=counts,
        tool_observations=[dict(chunk_id='703123',exit_code=0,kind='current_stage_listing'),
            dict(chunk_id='934e91',exit_code=1,kind='rg_old_portable_tools_tmp_access_denied_no_mutation'),
            dict(chunk_id='6e52bf',session_id=99542,terminal_exit=None,raw_updates=7227,invocation_new_updates=27027,cumulative_wall_seconds=62491.43743099994),
            dict(chunk_id='cd43af',exit_code=0,GPU_free_MiB=1394,GPU_utilization_percent=90),
            dict(chunk_id='23d551',exit_code=0,outer_batch_output_truncated=True,used_as_full_paper_read=False),
            dict(chunk_id='a229bc',exit_code=0,rendered_physical_pages=13),
            dict(chunk_id='c3cadd',exit_code=0,public_web_HTTP=200,public_README_HTTP=200),
            dict(chunk_id='418889',exit_code=1,kind='PowerShell_inline_Python_quote_loss',
                error='SyntaxError: invalid syntax; Path(D:/MRI/...) arrived without string quotes',files_written=False),
            dict(chunk_id='399c97',exit_code=0,kind='saved_script_original_PDF_table4_detail_render'),
            dict(chunk_id='3d1f4b',exit_code=0,public_table_rows_checked=52),
            dict(chunk_id='bd10f3',session_id=99542,terminal_exit=None,raw_updates=7425,invocation_new_updates=27225,cumulative_wall_seconds=62966.393889699946),
            dict(chunk_id='a226a6',exit_code=0,GPU_free_MiB=1394,GPU_utilization_percent=92,root_hashes_unchanged=True)],
        full_text_current_tool_batches=current,inherited_full_text_batches=inherited,
        current_invocation_newly_completed_physical_pages=[29,30,31,34,36,38,41,42],
        current_invocation_distinct_full_pages_read=17,
        actual_visual_reviews=[dict(review_group='view_image_batch_01',physical_pages=[1,3,5,6]),
            dict(review_group='view_image_batch_02',physical_pages=[9,13,15,16]),
            dict(review_group='view_image_batch_03',physical_pages=[21,25,32,35,40])],
        additional_same_page_detail_review=dict(physical_page=15,review_group='view_image_table4_detail',
            source=client.base.entry(HERE/'visual_attempt01/mirto_page015_table4_detail.png')),
        corrected_assistant_reading_error=dict(wrong_claim='Table4 cDDPM20 mean is .503 and conflicts with appendix',
            correct_reading='Mean .519; CI [.503,.535]; no table conflict',public_correction_delivered=True,
            original_handoff_0_519_was_correct=True),
        goal_observation=dict(status='active',tokensUsed_observed=41823734,scientific_objective_met=False),
        automatic_approval_review_rejections_received=0)
    client.base.new(HERE/'ACTUAL_OBSERVATIONS.json',obs)
    docs=[Path(__file__)]+[HERE/n for n in ['PROTOCOL.md','PRIMARY_SELECTION.md','VISUAL_AND_FALLBACK_PLAN.md',
        'CPU_AUDIT_PLAN.md','PRIMARY_READING.md','PATIENT_TASK_CONTROLS.md','RESULT.md','NEXT_STAGE_HANDOFF.md',
        'VISIBLE_DIALOGUE.md','USER_PROVIDED_HANDOFF.md','ACTUAL_OBSERVATIONS.json','primary_attempt01/receipt.json',
        'visual_attempt01/receipt.json','visual_attempt01/table4_detail_receipt.json','author_identity_attempt01/receipt.json',
        'author_web_attempt01/receipt.json','cpu_audit_attempt01/receipt.json']]
    reading=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],**counts,
        paper=dict(indexed_identity=r['indexed_record'],PDF_source=r['file'],
            text_pages_read=[dict(**b,actual_text_read=True,**mapping[b['physical_page']]) for b in r['page_texts']],
            visual_pages_reviewed=[dict(**b,actual_visual_reviewed=True) for b in visual['records']],
            all43_text_pages_read=True,pure_reference_pages=[23,24],all43_pages_visually_reviewed=False,
            additional_detail_review=obs['additional_same_page_detail_review'],author_code_reproduced=False),
        source_bindings=[client.base.entry(p) for p in docs],author_READMEs_read=1,author_source_files_read=0,
        author_default_branch_visible_state='placeholder',complete_repository_tree_verified=False,
        prior_extraction_render_and_failed_API_receipts_not_rewritten=True,scientific_claim_confirmed=False)
    client.base.new(HERE/'READING_PROVENANCE.json',reading)
    roots=[]
    for path,expected in [('D:/MRI/.gitignore','7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524'),
        ('D:/MRI/environment.yml','dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257')]:
        p=Path(path);assert sha(p)==expected;roots.append(dict(path=path,sha256=sha(p),previous_sha256=expected))
    zeros={k:0 for k in ['medical_arrays_loaded','model_checkpoint_arrays_loaded_from_disk','neural_forwards','MRI_neural_forwards',
        'GPU_forwards','real_medical_training_updates','head_fits','new_action_labels_generated','new_agents_delegated']}
    ledger=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],**counts,**zeros,
        source_bindings=[client.base.entry(p) for p in docs+[HERE/'READING_PROVENANCE.json',ROOT/'adaptive_compute_task_budget_prior_art_2026_10_08/ARCHIVE_PROOF.json']],
        root_files_observed=roots,resource_snapshot=resources,actual_observations=obs,
        original_training_terminal_exit=None,latest_raw_arm_updates=7425,latest_invocation_new_updates=27225,
        original_training_modified=False,current_original_contract=dict(per_arm_updates=19998,total_updates=39996,cumulative_wall_limit_hours=30),
        new_GPU_job_started=False,GPU_user_authorization_present=True,latest_GPU_free_MiB=1394,
        confirmation_patients_opened=False,lockedIXI_opened=False,publication_claim_confirmed=False,goal_status='active',
        previous_frozen_evidence_files_expected=5292,automatic_approval_review_rejections_received=0,
        CPU_public_arithmetic_is_not_MRI_effect_evidence=True,known_failed_executions_preserved=True)
    client.base.new(HERE/'EXECUTION_LEDGER.json',ledger)
    print(json.dumps(dict(complete=True,**counts,resource_snapshot=resources,goal_status='active',publication_claim_confirmed=False)),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
