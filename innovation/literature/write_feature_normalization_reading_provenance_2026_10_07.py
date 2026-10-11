"""Write completed reading/visual evidence separately from acquisition historical false flags."""
import hashlib,json,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'source_cache/feature_normalization_primary_2026-10-07'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');path=OUT/'reading_provenance_2026_10_07.json';assert not path.exists()
    aq=json.loads((OUT/'acquisition_attempt01.json').read_text(encoding='utf-8'))
    render=json.loads((OUT/'formula_rendering_attempt01.json').read_text(encoding='utf-8'))
    rows=[]
    for p in aq['papers']:
        assert p['fulltext_acquired'] and sha(OUT/p['pdf_file'])==p['pdf_sha256'] and sha(OUT/p['page_text_file'])==p['page_text_sha256']
        visual=next(v for v in render['formula_pages'] if v['key']==p['key']);assert sha(OUT/visual['image_file'])==visual['image_sha256']
        rows.append(dict(key=p['key'],source_url=p['url'],pdf_file=p['pdf_file'],pdf_sha256=p['pdf_sha256'],
                         text_file=p['text_file'],text_sha256=p['text_sha256'],page_text_file=p['page_text_file'],page_text_sha256=p['page_text_sha256'],
                         pages_textually_read=list(range(1,p['pages']+1)),actual_reading_completed=True,
                         actual_reading_scope='All extractable page text including references, tables and captions; only specified formula page visually reviewed',
                         formula_visual_review=dict(page=visual['page'],image_file=visual['image_file'],image_sha256=visual['image_sha256'],
                                                    actual_view_image_completed=True,formula_and_axes_readable=True),
                         author_code_or_training_reproduced=False,all_other_figures_visually_reviewed=False))
    assert len(rows)==3 and sum(len(r['pages_textually_read']) for r in rows)==33
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],script_sha256=sha(__file__),
           acquisition_sha256=sha(OUT/'acquisition_attempt01.json'),rendering_sha256=sha(OUT/'formula_rendering_attempt01.json'),
           report_file='../../2026-10-07_feature_normalization_primary_reading.md',
           report_sha256=sha(ROOT/'2026-10-07_feature_normalization_primary_reading.md'),papers=rows,
           primary_texts_read=3,total_pdf_pages_textually_read=33,historical_acquisition_and_render_visual_flags_preserved=True,
           truncated_first_adain_pages_2_and_3_reread=True,initial_omitted_groupnorm_output_reread_all_pages=True,
           referenced_studies_not_counted_as_read=True,root_environment_modified=False)
    with path.open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(dict(complete=True,primary_texts_read=3,pages_textually_read=33,formula_pages_visually_reviewed=3)))
if __name__=='__main__':main()
