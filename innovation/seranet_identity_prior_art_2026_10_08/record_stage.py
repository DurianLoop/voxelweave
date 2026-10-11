"""Bind genuinely read pages and observed exits; no live training weights or medical arrays."""
import sys,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
import query_seranet_stdlib_v3 as prior
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
base=prior.base

def read(p):return json.loads(p.read_text(encoding='utf-8'))

def main():
    sys.stdout.reconfigure(encoding='utf-8');base.own_priority();resources=prior.resource_guard()
    obs=read(HERE/'ACTUAL_OBSERVATIONS.json')
    audit=read(HERE/'recurrent_audit_attempt02/receipt.json')
    sad=read(HERE/'table_audit_attempt01/receipt.json')
    assert audit['complete'] and sad['complete'] and not audit['errors'] and not sad['errors']
    assert len(audit['SERANet_source_mean_inconsistencies'])==1 and not audit['SERANet_printed_means_rounding_consistent']
    docs=[]
    configs=[('sadfn','primary_attempt01',16,[16],[1,2,6,7,8,9,10,11,12,13,14,15],'1804.01210v1',
              ['e02a2f','f7b0f0','265470','3bcc75','186f13'],'user_provided_handoff'),
             ('seranet_candidate','primary_attempt02',13,[13],[1,2,4,5,6,7,8],'1812.02068v2',
              ['386e3b','5769ff','805fc9','1f9d33'],'actual_current_tools'),
             ('teacher_forcing','primary_attempt02',16,[15,16],[1,4,5,6,7,10,13],'2011.13614v1',
              ['ce8f93','4a3699','9d6253','58fd26','7fcc8a'],'actual_current_tools')]
    for key,sub,total,refs,visual,version,chunks,origin in configs:
        record=next(r for r in read(HERE/sub/'receipt.json')['records'] if r['key']==key)
        assert record['complete'] and record['physical_pages']==total
        src=HERE/sub/f'{key}.pdf'
        assert base.entry(src)==record['file']
        text_records=[dict(physical_page=n,actually_read=True,**base.entry(HERE/sub/f'{key}_page{n:03d}.txt')) for n in range(1,total+1)]
        visdir='visual_attempt01' if key=='sadfn' else 'visual_attempt02'
        images=[dict(physical_page=n,actually_viewed=True,**base.entry(HERE/visdir/f'{key}_page{n:03d}.png')) for n in visual]
        docs.append(dict(paper=key,actual_version=version,PDF_binding=base.entry(src),physical_pages=total,
            full_text_pages_actually_read=list(range(1,total+1)),reference_only_pages=refs,
            page_text_bindings=text_records,visual_pages_actually_viewed=visual,image_bindings=images,
            actual_text_chunks=chunks,reading_origin=origin,author_code_read=False,author_training_reproduced=False))
    sources=[Path(__file__),HERE/'PROTOCOL.md',HERE/'PRIMARY_READING.md',HERE/'ACTUAL_OBSERVATIONS.json',
       HERE/'USER_PROVIDED_HANDOFF.md',HERE/'INNOVATION_AND_MATCHED_CONTROLS.md',HERE/'ARITHMETIC_SOURCE_DIFFERENCE_REPAIR.md',
       HERE/'recurrent_audit_attempt02/receipt.json',HERE/'table_audit_attempt01/receipt.json']
    reading=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],records=docs,
        source_bindings=[base.entry(p) for p in sources],new_primary_papers_read=3,new_full_text_pages_read=45,
        current_continuation_new_text_pages=29,reference_only_pages_read=4,main_or_mixed_pages_read=41,
        visual_pages_reviewed=26,additional_detail_images_actually_viewed=2,detail_images_add_unique_pages=0,
        detail_image_bindings=[base.entry(p) for p in sorted((HERE/'table_visual_attempt01').glob('*.png'))],
        inherited_index_titles_screened=10,inherited_index_usable_abstracts_read=3,
        current_index_title_records_screened=5,current_index_abstract_records_read=0,
        search_scope='OpenAlex search=SERANet, metadata search rather than exact title filter',
        SERANet_identity_verified=True,chapter_fulltext_read=False,systematic_review=False,
        medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,publication_claim_confirmed=False,goal_status='active')
    base.new(HERE/'READING_PROVENANCE.json',reading)
    roots=[]
    for name,expected in [('.gitignore','7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524'),
                         ('environment.yml','dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257')]:
        p=ROOT.parent/name;actual=hashlib.sha256(p.read_bytes()).hexdigest();assert actual==expected
        roots.append(dict(path=str(p),sha256=actual,previous_sha256=expected))
    ledger=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[base.entry(p) for p in [*sources,HERE/'READING_PROVENANCE.json',HERE/'RESULT.md',
            HERE/'NEXT_STAGE_HANDOFF.md',HERE/'VISIBLE_DIALOGUE.md',ROOT/'experiments/mc_rc_reference_resources_2026_10_07.py']],
        new_primary_papers_read=3,new_full_text_pages_read=45,reference_only_pages_read=4,visual_pages_reviewed=26,
        additional_detail_images_viewed=2,SERANet_found_and_identity_verified=True,
        actual_execution_observations=obs,current_public_table_arithmetic_complete=True,
        source_mean_inconsistencies=audit['SERANet_source_mean_inconsistencies'],source_narrative_differences=audit['source_differences'],
        all_source_printed_summaries_consistent=False,resource_snapshot=resources,root_files_observed=roots,
        original_training_terminal_exit=None,original_training_modified=False,
        original_training_terminated_restarted_or_migrated=False,GPU_authorization_retained=True,new_GPU_job_started=False,
        medical_arrays_loaded=0,model_checkpoint_arrays_loaded_from_disk=0,neural_forwards=0,MRI_neural_forwards=0,GPU_forwards=0,
        real_medical_training_updates=0,head_fits=0,new_action_labels_generated=0,new_agents_delegated=0,
        confirmation_patients_opened=False,lockedIXI_opened=False,full_action_cost_measured=False,
        actual_new_MRI_task_benefit_measured=False,publication_claim_confirmed=False,goal_status='active',
        current_goal_turn_classification='progress',automatic_approval_review_rejections_received=0)
    base.new(HERE/'EXECUTION_LEDGER.json',ledger)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<30_000_000
    print(json.dumps(dict(complete=True,papers=3,text_pages=45,unique_visual_pages=26,source_mean_inconsistencies=1,
        resource_snapshot=resources,root_hashes_unchanged=True,medical_arrays_loaded=0,goal_status='active')),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
