"""Register already performed focused PDF reading and actual three-page visual checks."""
import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'literature/source_cache/masked_normalization_primary_2026-10-03'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    extraction=SRC/'extraction_attempt_03.json';e=json.loads(extraction.read_text(encoding='utf-8'))
    report=ROOT/'literature/2026-10-03_masked_normalization_primary_reading.md'
    reading_ranges={'region_normalization':list(range(1,9)),'partial_convolution':[3,5,6,7,8,9,12,13,14],'normalization_equivariance':list(range(1,11))+[21]}
    identities={'region_normalization':('Region Normalization for Image Inpainting','10.1609/aaai.v34i07.6967'),
                'partial_convolution':('Image Inpainting for Irregular Holes Using Partial Convolutions','10.1007/978-3-030-01252-6_6'),
                'normalization_equivariance':('Normalization-Equivariant Neural Networks with Application to Image Denoising','10.52202/075280-0249')}
    render=json.loads((SRC/'rendering_provenance.json').read_text(encoding='utf-8'));papers=[]
    for item in e['papers']:
        key=item['key'];pages=json.loads((SRC/item['page_text_file']).read_text(encoding='utf-8'))
        for kind in ('pdf','text','page_text'):assert sha(SRC/item[kind+'_file'])==item[kind+'_sha256']
        actual=[p for p in pages if p['page'] in reading_ranges[key]];assert len(actual)==len(reading_ranges[key])
        visual=next(v for v in render['outputs'] if v['key']==key);assert sha(SRC/visual['png'])==visual['sha256']
        papers.append(dict(key=key,title=identities[key][0],doi=identities[key][1],source_url=item['source_url'],
                           pdf=item['pdf_file'],pdf_sha256=item['pdf_sha256'],text=item['text_file'],text_sha256=item['text_sha256'],
                           pages=item['page_text_file'],pages_sha256=item['page_text_sha256'],total_pdf_pages=len(pages),
                           actual_read_pages=reading_ranges[key],actual_page_anchors=actual,actual_focused_primary_reading_completed=True,
                           all_pdf_pages_read=(len(actual)==len(pages)),visual_pages_reviewed=[visual['page']],visual_png=visual['png'],visual_png_sha256=visual['sha256'],
                           author_experiments_independently_reproduced=False,separate_supplement_read=False))
    out=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),extraction_manifest_sha256=sha(extraction),
             report=report.relative_to(ROOT).as_posix(),report_sha256=sha(report),new_public_primary_pdfs=3,new_primary_papers_focused_read=3,
             actual_pdf_page_anchors=sum(len(x['actual_read_pages']) for x in papers),actual_visual_pages_reviewed=3,papers=papers,
             original_rendering_manifest_sha256=sha(SRC/'rendering_provenance.json'),
             prior_rendering_visual_flag_left_as_historical_state=True,visual_review_completed=True,
             retained_failures=[dict(file=n,sha256=sha(SRC/n)) for n in ('attempt_01.json','extraction_failed_attempt_02.json','extraction_script_before_href_fix.txt')],
             inherited_reading_scope='Prior stage handoff plus current targeted text/formula recheck; three PNGs re-viewed in current continuation.',
             publication_claim_confirmed=False)
    p=SRC/'reading_provenance.json';assert not p.exists();p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in out.items() if k not in ('papers','retained_failures')},ensure_ascii=False))
if __name__=='__main__':main()
