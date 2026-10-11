"""Fetch only title-verified public originals; extraction is not a reading claim."""
import concurrent.futures, hashlib, json, subprocess, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'literature/source_cache/direct_observed_primary_2026-10-07'
ITEMS = [('sparsity_invariant', 'Sparsity Invariant CNNs', 'https://arxiv.org/pdf/1708.06500'),
         ('confidence_propagation', 'Confidence Propagation through CNNs for Guided Sparse Depth Regression', 'https://arxiv.org/pdf/1811.01791')]

def fetch(item):
    key, title, url = item
    r = dict(key=key, title=title, requested_url=url, reading_performed=False)
    try:
        identity=json.loads((OUT/'identity_attempt01.json').read_text(encoding='utf-8'))
        record=next(x for x in identity['records'] if x['key']==key)
        assert any(x['title']==title and any(y['pdf_url']==url for y in x['locations']) for x in record['results'])
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(urllib.request.Request(url, headers={'User-Agent':'MRI-local-research/1.0'}),timeout=30) as response:
            b=response.read(32_000_001)
            r.update(status=response.status, final_url=response.url, content_type=response.headers.get('Content-Type'))
        assert len(b)<=32_000_000 and b.startswith(b'%PDF-')
        pdf=OUT/(key+'.pdf'); assert not pdf.exists(); pdf.write_bytes(b)
        info=subprocess.run(['pdfinfo',str(pdf)],capture_output=True,text=True,timeout=30,check=True)
        (OUT/(key+'_pdfinfo.txt')).write_text(info.stdout,encoding='utf-8')
        textfile=OUT/(key+'_layout.txt')
        subprocess.run(['pdftotext','-layout',str(pdf),str(textfile)],timeout=30,check=True)
        pages=textfile.read_text(encoding='utf-8').split('\f')
        if not pages[-1].strip(): pages.pop()
        pagedir=OUT/(key+'_pages'); pagedir.mkdir(exist_ok=False)
        for n,page in enumerate(pages,1): (pagedir/f'page_{n:02d}.txt').write_text(page,encoding='utf-8')
        r.update(success=True, pdf_file=pdf.relative_to(ROOT).as_posix(), pdf_bytes=len(b),
                 pdf_sha256=hashlib.sha256(b).hexdigest(), extracted_pages=len(pages),
                 text_file=textfile.relative_to(ROOT).as_posix(), text_sha256=hashlib.sha256(textfile.read_bytes()).hexdigest())
    except Exception as e: r.update(success=False,error=f'{type(e).__name__}: {e}')
    return r

def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool: rows=list(pool.map(fetch,ITEMS))
    with (OUT/'download_attempt01.json').open('x',encoding='utf-8') as f:
        json.dump(dict(created_utc=datetime.now(timezone.utc).isoformat(),records=rows,
                       script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),f,ensure_ascii=False,indent=2)
    print(json.dumps(rows,ensure_ascii=False))
    return int(not all(x['success'] for x in rows))

if __name__=='__main__': raise SystemExit(main())
