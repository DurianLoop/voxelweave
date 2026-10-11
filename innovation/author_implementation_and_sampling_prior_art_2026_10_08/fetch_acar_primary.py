"""Retrieve only the PDF actually linked by the matched institutional record."""
import sys,json,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'primary_attempt01'
sys.path.insert(0,str(ROOT/'seranet_identity_prior_art_2026_10_08'))
import fetch_selected_stdlib as downloader
import query_seranet_stdlib_v3 as client

def main():
    sys.stdout.reconfigure(encoding='utf-8');client.base.own_priority();client.resource_guard()
    index=HERE/'index_attempt01/receipt.json'
    q=json.loads(index.read_text(encoding='utf-8'))
    row=next(r for r in q['records'] if r['key']=='acar_bilkent')
    assert row['complete']
    md=row['metadata']
    assert next(m['content'] for m in md if m.get('name')=='citation_doi')=='10.1007/978-3-031-17247-2_6'
    urls=[m['content'] for m in md if m.get('name')=='citation_pdf_url']
    assert len(urls)==1 and urls[0] in row['public_links']
    OUT.mkdir(exist_ok=False);downloader.OUT=OUT;tick=time.perf_counter()
    record=downloader.fetch(('acar',row,urls[0]))
    if record['complete']:
        sys.path.insert(0,str(ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08/site_packages'))
        import pypdfium2 as pdfium
        doc=pdfium.PdfDocument(str(ROOT/record['file']['path']))
        record['physical_pages']=len(doc);record['page_texts']=[]
        for n in range(len(doc)):
            client.resource_guard();page=doc[n];tp=page.get_textpage();p=OUT/f'acar_page{n+1:03d}.txt'
            with p.open('x',encoding='utf-8') as f:f.write(tp.get_text_range())
            record['page_texts'].append(dict(physical_page=n+1,text_read=False,**client.base.entry(p)))
            tp.close();page.close()
        doc.close()
    result=dict(complete=record['complete'],errors=record['errors'],records=[record],
        source_bindings=[client.base.entry(p) for p in (Path(__file__),HERE/'PRIMARY_SELECTION.md',index)],
        elapsed_seconds=time.perf_counter()-tick,resource_snapshot=client.resource_guard(),
        new_primary_papers_read=0,medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0)
    client.base.new(OUT/'receipt.json',result)
    print(json.dumps({k:record.get(k) for k in ('key','complete','HTTP_status','physical_pages','file','errors')},ensure_ascii=False))
    return int(not result['complete'])
if __name__=='__main__':raise SystemExit(main())
