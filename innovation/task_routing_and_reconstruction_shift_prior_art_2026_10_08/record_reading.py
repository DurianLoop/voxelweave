"""Bind actual complete-page and visual scopes; extraction flags stay immutable."""
import sys,time,json
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'task_adaptation_compute_prior_art_2026_10_08'))
import query_primary as base
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def main():
    sys.stdout.reconfigure(encoding='utf-8');tick=time.perf_counter();resource_guard()
    t= json.loads((HERE/'tadt_text_attempt05/receipt.json').read_text(encoding='utf-8'))
    m= json.loads((HERE/'primary_attempt02/receipt.json').read_text(encoding='utf-8'))
    v= json.loads((HERE/'visual_attempt01/receipt.json').read_text(encoding='utf-8'))
    assert t['complete'] and t['local_title_authors_version_identity_passed'] and v['complete']
    mr=next(r for r in m['records'] if r['key']=='medical_shift');assert mr['complete'] and mr['physical_pages']==39
    pages={'tadt':list(range(1,17)),'medical_shift':list(range(1,14))+[21,22,23,28,29]}
    texts=[];sources=[Path(__file__),HERE/'PRIMARY_READING.md',HERE/'PROTOCOL.md',HERE/'tadt_text_attempt05/receipt.json',HERE/'primary_attempt02/receipt.json',HERE/'visual_attempt01/receipt.json']
    for key,nums in pages.items():
        for n in nums:
            p=(HERE/'tadt_text_attempt05'/f'tadt_page{n:03d}.txt') if key=='tadt' else HERE/'primary_attempt02'/f'medical_shift_page{n:03d}.txt'
            if key=='tadt' and n==1:p=HERE/'tadt_size_verified_attempt03/tadt_page001.txt'
            texts.append(dict(paper=key,physical_page=n,text_read=True,**base.entry(p)));sources.append(p)
    visuals=[]
    for row in v['records']:
        assert row['physical_page'] in pages[row['paper']]
        p=ROOT/row['image']['path'];visuals.append(dict(paper=row['paper'],physical_page=row['physical_page'],visual_reviewed=True,image=base.entry(p)));sources.append(p)
    assert len(texts)==34 and len(visuals)==15 and len({(r['paper'],r['physical_page']) for r in texts})==34
    first=(HERE/'primary_attempt02/medical_shift_page001.txt').read_text(encoding='utf-8')
    assert 'Evaluating the Impact of Medical Image Reconstruction on' in first and 'arXiv:2604.10904v1' in first
    q=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],source_bindings=[base.entry(p) for p in sources],
        new_primary_papers_read=2,new_full_text_pages_read=34,main_text_pages_read=20,selected_appendix_text_pages_read=7,
        ancillary_reference_and_visual_caption_text_pages_read=7,visual_pages_reviewed=15,text_page_bindings=texts,visual_page_bindings=visuals,
        tadt_text_pages_read=16,tadt_visual_pages_reviewed=8,medical_text_pages_read=18,medical_visual_pages_reviewed=7,
        tadt_all16_text_read_not_all_visual_examples_reviewed=True,medical_entire39_pages_not_claimed_read=True,
        medical_unread_physical_pages=[n for n in range(1,40) if n not in pages['medical_shift']],author_code_not_read=True,
        network_index_requests=0,repeated_abstracts_not_new_screening=True,TADT_body_ETag_match=False,
        TADT_local_title_authors_arxiv_version_identity_passed=True,original_failed_encoding_records_retained=True,
        interpretation_of_equations_verified_from_PDF_images=True,new_MRI_benefit_measured=False,
        medical_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,training_updates=0,
        publication_claim_confirmed=False,goal_status='active',elapsed_seconds=time.perf_counter()-tick)
    base.new(HERE/'READING_PROVENANCE.json',q)
    print(json.dumps(dict(complete=True,new_primary_papers_read=2,new_full_text_pages_read=34,visual_pages_reviewed=15)),flush=True);return 0
if __name__=='__main__':raise SystemExit(main())
