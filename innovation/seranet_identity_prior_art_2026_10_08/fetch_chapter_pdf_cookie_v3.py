"""Same actual citation URL, now with a standard anonymous cookie jar for this process."""
import sys,json,time,http.cookiejar
from pathlib import Path
from datetime import datetime,timezone
from urllib.request import build_opener as default_opener,HTTPCookieProcessor
import fetch_selected_stdlib as prior
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'chapter_pdf_attempt03'
base=prior.base
def anonymous_opener(*handlers):
    return default_opener(*handlers,HTTPCookieProcessor(http.cookiejar.CookieJar()))
def main():
    sys.stdout.reconfigure(encoding='utf-8');prior.resource_guard();OUT.mkdir(exist_ok=False);tick=time.perf_counter()
    # Only this newly launched client's runtime adapter changes. Bound prior source files remain untouched.
    prior.OUT=OUT;prior.build_opener=anonymous_opener
    metadata=HERE/'publisher_metadata_attempt01/extracted_metadata.json';q=prior.read(metadata)
    assert q['complete'] and not q['errors'] and q['metadata']['citation_doi']==['10.1007/978-3-031-17247-2_6']
    urls=q['metadata']['citation_pdf_url'];assert len(urls)==1
    index=HERE/'index_attempt03/receipt.json';chapter=next(e for r in prior.read(index)['records'] for e in r.get('entries',[]) if e.get('DOI')=='10.1007/978-3-031-17247-2_6')
    row=prior.fetch(('acar_segmentation_aware',chapter,urls[0]))
    if row['complete']:
        sys.path.insert(0,str(ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08/site_packages'))
        import pypdfium2 as pdfium
        doc=pdfium.PdfDocument(str(ROOT/row['file']['path']));row['physical_pages']=len(doc);row['page_texts']=[]
        for n in range(len(doc)):
            prior.resource_guard();page=doc[n];tp=page.get_textpage();p=OUT/f'acar_segmentation_aware_page{n+1:03d}.txt'
            with p.open('x',encoding='utf-8') as f:f.write(tp.get_text_range())
            row['page_texts'].append(dict(physical_page=n+1,text_read=False,**base.entry(p)));tp.close();page.close()
        doc.close()
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=row['complete'],errors=row['errors'],records=[row],
        source_bindings=[base.entry(p) for p in (Path(__file__),HERE/'CHAPTER_COOKIE_CLIENT_REPAIR.md',metadata,index,
            HERE/'fetch_selected_stdlib.py',HERE/'chapter_pdf_attempt02/receipt.json')],
        anonymous_cookie_memory_only=True,authentication_used=False,TLS_verification_disabled=False,automatic_retries=False,
        new_primary_papers_read=0,medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,new_agents_delegated=0,
        elapsed_seconds=time.perf_counter()-tick)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<30_000_000
    base.new(OUT/'receipt.json',result)
    print(json.dumps({k:row.get(k) for k in ['complete','HTTP_status','effective_url','physical_pages','file','errors']},ensure_ascii=False),flush=True)
    return int(not result['complete'])
if __name__=='__main__':raise SystemExit(main())
