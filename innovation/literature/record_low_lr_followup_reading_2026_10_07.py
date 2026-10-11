"""Record actual incremental reading without rewriting acquisition-time snapshots."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/low_lr_followup_reading_2026-10-07'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    cache=ROOT/'literature/source_cache/hcc_sr_task_primary_2026-10-07'
    supplement=cache/'supplement_attempt01'
    queries=ROOT/'literature/source_cache/action_utility_followup_2026-10-07/attempt01.json'
    source=json.loads(queries.read_text(encoding='utf-8'))
    seen={(x['source'],x['id']) for q in source['queries'] for x in q['items']}
    assert len(seen)==22 and sum(q['returned'] for q in source['queries'])==24
    pages=json.loads((supplement/'physical_pages.json').read_text(encoding='utf-8'))
    blocks=json.loads((cache/'hcc_sr_task_blocks.json').read_text(encoding='utf-8'))
    assert [p['page'] for p in pages]==list(range(1,15)) and len(blocks)==161
    reports=[ROOT/'literature/2026-10-07_hcc_sr_task_primary_reading.md',ROOT/'literature/2026-10-07_action_utility_followup_reading.md']
    files=[cache/'hcc_sr_task_fulltext.xml',cache/'hcc_sr_task_blocks.json',supplement/'hcc_sr_task_supplement.pdf',queries,*reports]
    visual=[]
    for n in (2,3,6,11,7,13):
        p=supplement/f'physical_page_{n:02d}_render.png';assert p.is_file()
        visual.append(dict(physical_page=n,**entry(p),actual_visual_review=True,
                           observation_origin='current_continuation_view_image' if n in (7,13) else 'prior_model_user_provided_handoff_summary'))
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],script_sha256=sha(__file__),
        sources=[entry(p) for p in files],new_primary_papers_completed=1,new_primary_doi='10.3748/wjg.v31.i34.111541',
        textual_full_body_reading_origin='prior_model_handoff; key methods/tables/limitations rechecked in current continuation',
        jats_extraction_blocks=161,blocks_include_nested_duplicates_tables_references=True,
        supplement_physical_pages_textually_read=list(range(1,15)),visual_reviews=visual,
        all_original_figure_pixels_inspected=False,queries_returned_rows=24,unique_index_records=22,
        query_hit_counts=[q['hit_count'] for q in source['queries']],new_abstracts_completed=3,
        new_abstract_dois=['10.20944/preprints202609.1256.v1','10.1016/j.jneumeth.2026.110834','10.1109/tmi.2026.3662706'],
        repeated_prior_abstracts=1,repeated_abstract_doi='10.1016/j.compmedimag.2026.102786',
        acquisition_snapshots_preserved=True,agentic_fulltext_acquired=False,agentic_failure='publisher HTTP 403',
        automatic_approval_rejection_for_agentic_request=False,authors_contacted=False,actual_training_updates=0,
        actual_gpu_updates=0,confirmation_patients_opened=False,publication_claim_confirmed=False)
    with (OUT/'actual_reading_and_visual_review_attempt01.json').open('x',encoding='utf-8') as f:
        json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({k:r[k] for k in ['complete','new_primary_papers_completed','new_abstracts_completed','queries_returned_rows','unique_index_records']},ensure_ascii=False))
    return 0
if __name__=='__main__':raise SystemExit(main())
