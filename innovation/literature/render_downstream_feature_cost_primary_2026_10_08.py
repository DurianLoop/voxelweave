"""Render source proof/table pages for actual visual inspection, no PDF authoring."""
import hashlib,json,sys,traceback
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'literature/source_cache/downstream_feature_cost_primary_2026-10-08'
OUT=BASE/'visual_attempt01'
sys.path.insert(0,str(ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08/site_packages'))
import pypdfium2 as pdfium


def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(exist_ok=False)
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],records=[],
        source_bindings=[entry(Path(__file__)),entry(BASE/'acquisition_attempt01.json'),
            entry(BASE/'prakash_arxiv_attempt01/acquisition_attempt01.json')],
        rendering_is_not_reading=True,medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,training_updates=0)
    try:
        for key,pdf,pages in (('noise2same_supplement',BASE/'noise2same_supplement.pdf',[1,2]),
                            ('prakash',BASE/'prakash_arxiv_attempt01/prakash_verified.pdf',[1,3])):
            doc=pdfium.PdfDocument(str(pdf))
            for number in pages:
                page=doc[number-1]
                bitmap=page.render(scale=1.8)
                picture=bitmap.to_pil()
                path=OUT/f'{key}_page{number:02d}.png'
                picture.save(path)
                r['records'].append(dict(key=key,physical_page=number,visually_reviewed=False,scale=1.8,
                    pixels=list(picture.size),**entry(path)))
                picture.close();bitmap.close();page.close()
            doc.close()
        r['complete']=True
    except Exception as exc:
        r['errors'].append(type(exc).__name__+': '+str(exc));r['traceback']=traceback.format_exc()
    r['saved_bytes']=sum(p.stat().st_size for p in OUT.iterdir() if p.is_file())
    assert r['saved_bytes']<5_000_000
    with (OUT/'render_attempt01.json').open('x',encoding='utf-8') as f:
        json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(dict(complete=r['complete'],errors=r['errors'],saved_bytes=r['saved_bytes'],rendered_pages=len(r['records'])),ensure_ascii=False),flush=True)
    return int(not r['complete'])


if __name__=='__main__':raise SystemExit(main())
