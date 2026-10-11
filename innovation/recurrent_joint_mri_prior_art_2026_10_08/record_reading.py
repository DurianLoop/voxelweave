"""Immutable record of pages actually read and images actually viewed, after the audit."""
import json,sys,time,unicodedata,re
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'task_adaptation_compute_prior_art_2026_10_08'))
import query_primary as base
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def compact(s):
    s=unicodedata.normalize('NFKD',s).casefold()
    return ''.join(c for c in s if c.isalnum())
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard();tick=time.perf_counter()
    download=read(HERE/'primary_attempt01/receipt.json');visual=read(HERE/'visual_attempt01/receipt.json')
    crops=read(HERE/'table_visual_attempt01/receipt.json');audit=read(HERE/'table_audit_attempt02/receipt.json')
    assert all(q['complete'] and not q['errors'] for q in [download,visual,crops,audit])
    assert audit['all_transcribed_rows_match_extracted_text'] and len(audit['source_printed_summary_inconsistencies'])==3
    rows=[]
    for key,ident,textpages,viewpages,unread in [
        ('mmar','2610.00553v1',list(range(1,31)),[1,6,7,8,10,14,16,17,19,20,22,23,24,25,26,27,28,29,30],[31,32,33,34]),
        ('xlstm_hved','2412.07804v3',[1,2,3,4,5],[1,2,3,4],[])]:
        d=next(r for r in download['records'] if r['key']==key)
        assert base.entry(ROOT/d['file']['path'])==d['file']
        first=(HERE/f'primary_attempt01/{key}_page001.txt').read_text(encoding='utf-8')
        assert ident in first and compact(d['indexed_record']['title']) in compact(first)
        assert all(compact(author) in compact(first) for author in d['indexed_record']['authors'])
        texts=[next(r for r in d['page_texts'] if r['physical_page']==n) for n in textpages]
        images=[next(r for r in visual['records'] if r['paper']==key and r['physical_page']==n) for n in viewpages]
        for b in texts:assert base.entry(ROOT/b['path'])=={k:b[k] for k in ['path','bytes','sha256']}
        for b in images:assert base.entry(ROOT/b['image']['path'])==b['image']
        rows.append(dict(paper=key,indexed_identity=d['indexed_record'],PDF_binding=d['file'],PDF_pages=d['physical_pages'],
            full_text_pages_actually_read=textpages,reference_only_pages_actually_read=[5] if key=='xlstm_hved' else [],
            remaining_pages_not_completely_read=unread,page_text_bindings=texts,
            visual_pages_actually_viewed=viewpages,rendered_image_bindings=images,
            source_identity_verified_from_first_page=True,author_code_read=False,author_experiments_reproduced=False))
    for c in crops['records']:assert base.entry(ROOT/c['image']['path'])==c['image']
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],records=rows,
        source_bindings=[base.entry(p) for p in [Path(__file__),HERE/'PROTOCOL.md',HERE/'PRIMARY_SELECTION.md',
            HERE/'PRIMARY_READING.md',HERE/'SUPERVISION_ROUTING_AND_CHECKPOINT_PREPARATION.md',
            HERE/'primary_attempt01/receipt.json',HERE/'visual_attempt01/receipt.json',
            HERE/'table_visual_attempt01/receipt.json',HERE/'table_audit_attempt02/receipt.json']],
        new_primary_papers_read=2,downloaded_and_extracted_pages=39,new_full_text_pages_read=35,
        full_text_main_or_figure_pages_read=34,reference_only_pages_read=1,visual_pages_reviewed=23,
        additional_detail_images_actually_viewed=7,detail_images_do_not_add_unique_pages=True,
        actual_text_tool_chunks=['527cb6','963c5c','d818d2','c76c94','b029b0','61cbb1','e9233b','6161ca','7840ab','6c3c1d','d7bf09'],
        duplicate_text_reread_not_counted_twice=True,
        actual_visual_tools='view_image: 23 original page images in four batches; seven detail crops in one batch',
        extraction_receipt_text_read_false_preserved=True,render_receipts_visual_reviewed_false_preserved=True,
        cropped_table_image_bindings=crops['records'],index_identity_audit=audit['index_identity_audit'],
        current_title_abstract_returned_records=16,current_title_abstract_unique_screened=16,
        current_papers_abstract_only=14,SERANet_found_and_read=False,systematic_review=False,
        source_arithmetic_inconsistencies=audit['source_printed_summary_inconsistencies'],
        public_table_arithmetic_only=True,patient_p_values_recomputed=False,
        medical_arrays_loaded=0,model_checkpoint_arrays_loaded_from_disk=0,neural_forwards=0,GPU_forwards=0,
        real_medical_training_updates=0,new_agents_delegated=0,actual_new_MRI_task_benefit_measured=False,
        publication_claim_confirmed=False,goal_status='active',elapsed_seconds=time.perf_counter()-tick)
    assert sum(len(r['full_text_pages_actually_read']) for r in rows)==35
    assert sum(len(r['visual_pages_actually_viewed']) for r in rows)==23
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<30_000_000
    base.new(HERE/'READING_PROVENANCE.json',result)
    print(json.dumps(dict(complete=True,new_primary_papers_read=2,new_full_text_pages_read=35,
        visual_pages_reviewed=23,detail_images=7,source_summary_inconsistencies=3,
        local_pdf_identities_verified=True)),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
