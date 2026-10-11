"""Freeze corrected-version textual reading and the actually viewed primary pages."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/'literature/source_cache/learning_to_defer_primary_attempt02_2026-10-07'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def e(p):return dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),bytes=p.stat().st_size)
def main():
    sys.stdout.reconfigure(encoding='utf-8');path=CACHE/'actual_reading_and_visual_review_attempt01.json';assert not path.exists()
    acquisition=json.loads((CACHE/'attempt01.json').read_text(encoding='utf-8'));assert all(p['fulltext_acquired'] and p['expected_title_verified'] for p in acquisition['papers'])
    papers=[]
    for key,pages,version in [('mozannar_sontag_pmlr_2020',12,'PMLR119 formal conference PDF; external Appendix B/C not acquired'),
                              ('madras_2018_verified',20,'arXiv1711.06664v3; included Appendix A-I')]:
        d=CACHE/key;index=json.loads((d/'physical_pages.json').read_text(encoding='utf-8'))
        assert [p['physical_page'] for p in index]==list(range(1,pages+1))
        papers.append(dict(key=key,version=version,source=e(d/'original.pdf'),text_index=e(d/'physical_pages.json'),
                           physical_pages_textually_read=list(range(1,pages+1)),all_figure_pixels_inspected=False))
    visual=[dict(key=key,physical_page=n,actual_view_image_completed=True,**e(CACHE/key/f'physical_page_{n:02d}_render.png'))
            for key,n in [('mozannar_sontag_pmlr_2020',4),('mozannar_sontag_pmlr_2020',8),('madras_2018_verified',3)]]
    report=ROOT/'literature/2026-10-07_learning_to_defer_primary_collision_reading.md'
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],script_sha256=sha(__file__),
           newly_completed_primary_papers=2,new_pdf_physical_pages_textually_read=32,papers=papers,visual_reviews=visual,
           report=e(report),acquisition_snapshot_preserved=True,wrong_identifier_download_preserved=True,
           wrong_identifier_paper_counted=False,over_budget_arxiv43pages_counted=False,neural_forwards=0,
           actual_training_updates=0,actual_gpu_updates=0,MRI_or_GT_loaded=0,publication_claim_confirmed=False)
    with path.open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({k:r[k] for k in ['complete','newly_completed_primary_papers','new_pdf_physical_pages_textually_read']}))
    return 0
if __name__=='__main__':raise SystemExit(main())
