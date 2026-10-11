"""Bind actually read pages and viewed images, distinct from extraction snapshots."""
import json,sys,time
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'task_adaptation_compute_prior_art_2026_10_08'))
import query_primary as base
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
    sys.stdout.reconfigure(encoding='utf-8');base.own_priority();resource_guard();tick=time.perf_counter()
    download=read(HERE/'primary_attempt01/receipt.json');visual=read(HERE/'visual_attempt01/receipt.json')
    audit=read(HERE/'table_audit_attempt01/receipt.json')
    assert all(q['complete'] and not q['errors'] for q in (download,visual,audit))
    rows=[]
    for key,ident,textpages,viewpages,unread in [('segnetmri','1805.02165v1',list(range(1,7)),[1,3,4,5,6],[7,8]),
       ('calibrationless','2105.09220v1',list(range(1,10)),[1,5,6,8,9],[10])]:
        d=next(r for r in download['records'] if r['key']==key)
        p=ROOT/d['file']['path'];assert base.entry(p)==d['file']
        page1=(HERE/f'primary_attempt01/{key}_page001.txt').read_text(encoding='utf-8')
        compact=' '.join(page1.split())
        assert d['indexed_record']['title'] in compact and 'arXiv:'+ident in compact
        assert all(name in compact for name in d['indexed_record']['authors'])
        texts=[next(r for r in d['page_texts'] if r['physical_page']==n) for n in textpages]
        images=[next(r for r in visual['records'] if r['paper']==key and r['physical_page']==n) for n in viewpages]
        for b in texts:assert base.entry(ROOT/b['path'])=={k:b[k] for k in ('path','bytes','sha256')}
        for b in images:assert base.entry(ROOT/b['image']['path'])==b['image']
        rows.append(dict(paper=key,indexed_identity=d['indexed_record'],PDF_binding=d['file'],
           PDF_pages=d['physical_pages'],full_text_pages_actually_read=textpages,
           physical_pages_with_main_text_read=len(textpages),remaining_pages_not_completely_read=unread,
           page_text_bindings=texts,visual_pages_actually_viewed=viewpages,rendered_image_bindings=images,
           source_identity_verified_by_local_first_page=True,
           author_code_read=False,author_experiments_independently_reproduced=False))
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],records=rows,
       source_bindings=[base.entry(p) for p in (Path(__file__),HERE/'PROTOCOL.md',HERE/'PRIMARY_SELECTION.md',
       HERE/'PRIMARY_READING.md',HERE/'SUPERVISION_EXPOSURE_AND_JOINT_CONTROL_PREPARATION.md',
       HERE/'primary_attempt01/receipt.json',HERE/'visual_attempt01/receipt.json',HERE/'table_audit_attempt01/receipt.json')],
       index_returned_records=9,index_unique_titles_abstracts_screened=8,index_requests=3,
       SERANet_found_and_read=False,systematic_review=False,new_primary_papers_read=2,
       downloaded_and_extracted_pages=18,new_full_text_pages_read=15,visual_pages_reviewed=10,
       extraction_receipt_read_false_preserved=True,render_receipt_visual_false_preserved=True,
       partial_aggregated_text_output_not_counted_until_complete_followup=True,
       actual_text_tool_chunks=['20a9a9','32ab76','53ab1a','a4aa2e','1ea60e','4fd662'],
       truncation_notes=['20a9a9 aggregate: segnetmri4/calibrationless1 completed by32ab76',
         '1ea60e cal7-10 output truncated: cal9 completed by4fd662; cal10 not counted'],
       visual_review_tools='Two actual view_image batches, five source pages in each batch.',
       medical_arrays_loaded=0,model_checkpoint_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,
       actual_new_MRI_task_benefit_measured=False,publication_claim_confirmed=False,
       goal_status='active',elapsed_seconds=time.perf_counter()-tick)
    assert sum(len(r['full_text_pages_actually_read']) for r in rows)==15
    assert sum(len(r['visual_pages_actually_viewed']) for r in rows)==10
    base.new(HERE/'READING_PROVENANCE.json',result)
    print(json.dumps(dict(complete=True,new_primary_papers_read=2,new_full_text_pages_read=15,visual_pages_reviewed=10,
       local_pdf_identities_verified=True)),flush=True);return 0
if __name__=='__main__':raise SystemExit(main())

