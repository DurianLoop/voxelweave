"""Use the actual official-page citation_pdf_url, distinct from the failed Crossref URL."""
import sys,json,time
from pathlib import Path
from datetime import datetime,timezone
import fetch_selected_stdlib as prior
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'chapter_pdf_attempt02'
base=prior.base
def main():
    sys.stdout.reconfigure(encoding='utf-8');prior.resource_guard();OUT.mkdir(exist_ok=False);prior.OUT=OUT;tick=time.perf_counter()
    metadata=HERE/'publisher_metadata_attempt01/extracted_metadata.json';q=prior.read(metadata)
    assert q['complete'] and not q['errors'] and q['metadata']['citation_doi']==['10.1007/978-3-031-17247-2_6']
    urls=q['metadata']['citation_pdf_url'];assert len(urls)==1 and urls[0].startswith('https://link.springer.com/content/pdf/')
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
        source_bindings=[base.entry(p) for p in (Path(__file__),HERE/'CHAPTER_PDF_SELECTION_V2.md',metadata,index,HERE/'fetch_selected_stdlib.py')],
        new_primary_papers_read=0,medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,new_agents_delegated=0,
        elapsed_seconds=time.perf_counter()-tick)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<30_000_000
    base.new(OUT/'receipt.json',result)
    print(json.dumps({k:row.get(k) for k in ['complete','HTTP_status','effective_url','physical_pages','file','errors']},ensure_ascii=False),flush=True)
    return int(not result['complete'])
if __name__=='__main__':raise SystemExit(main())
