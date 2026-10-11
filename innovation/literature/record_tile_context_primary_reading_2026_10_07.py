"""Separate actual reading/visual review from immutable acquisition records."""
import hashlib,json,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'source_cache/tile_context_visual_review_2026-10-07'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');path=OUT/'actual_reading_and_visual_review_attempt01.json';assert not path.exists()
    exact=ROOT/'source_cache/tile_context_alternates_2026-10-07/exact_tile_blocks.json'
    kin=ROOT/'source_cache/kernel_normalization_primary_2026-10-07/kin_pages.json'
    tin=OUT/'tin_physical_pages.json';renders=json.loads((OUT/'extraction_and_render_attempt01.json').read_text(encoding='utf-8'))
    assert len(json.loads(exact.read_text(encoding='utf-8')))==176
    assert len(json.loads(kin.read_text(encoding='utf-8')))==24 and len(json.loads(tin.read_text(encoding='utf-8')))==10
    papers=[dict(key='exact_tile',format='original_public_XML',actual_reading_completed=True,blocks_read=list(range(176)),
        file=exact.relative_to(ROOT).as_posix(),sha256=sha(exact),original_images_visually_read=False),
        dict(key='kin',format='original_fixed_version_PDF',version='2208.10730v1',actual_reading_completed=True,
            physical_pages_text_read=list(range(1,25)),supplement_physical_pages=list(range(17,25)),
            file=kin.relative_to(ROOT).as_posix(),sha256=sha(kin)),
        dict(key='tin',format='original_fixed_version_PDF',version='2103.11784v3',actual_reading_completed=True,
            physical_pages_text_read=list(range(1,11)),file=tin.relative_to(ROOT).as_posix(),sha256=sha(tin),
            previous_incorrect_formfeed_page_count_preserved=12)]
    visual=[]
    for row in renders['rendered']:
        png=OUT/row['png_file'];assert sha(png)==row['png_sha256'] and sha(row['source_pdf'])==row['source_pdf_sha256']
        visual.append(dict(**row,actual_visual_review=True,
            review_note={'tin_formula':'TIN Eq2 uses thumbnail statistics to normalize candidate patch, matching external-reference normalization form.',
                         'kin_formula':'Mean and standard deviation are separately averaged over cached neighboring patches, Eq5-7.',
                         'kin_glioma_table':'Table2 CUT test FID improves but PIQE and histogram correlation worsen; preserve mixed results.',
                         'kin_downstream':'Supplement reports deliberately chosen seam patches, 98.8/88.4/99.2 classification accuracies; not MRI/Dice evidence.'}[row['key']]))
    report=ROOT/'2026-10-07_exact_tiling_TIN_KIN_primary_reading.md'
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],script_sha256=sha(__file__),
        primary_papers_newly_read=3,pdf_physical_pages_textually_read=34,primary_XML_extraction_blocks_read=176,
        physical_PDF_pages_visually_reviewed=4,papers=papers,visual_reviews=visual,
        full_reading_report_file=report.name,full_reading_report_sha256=sha(report),
        acquired_but_body_not_read=['kernel_norm_2205.10089v4'],
        metadata_only_failed_fulltext=['patch_mr_norm_PMC3892712'],
        all_other_figure_pixels_not_reviewed=True,author_experiments_reproduced=False,
        external_reference_normalization_first_claim_rejected=True,publication_claim_confirmed=False)
    path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:r[k] for k in ('complete','primary_papers_newly_read','pdf_physical_pages_textually_read','physical_PDF_pages_visually_reviewed')}))
if __name__=='__main__':main()
