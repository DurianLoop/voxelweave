"""Fetch only two exact PDF URLs returned by the actual metadata query."""
import sys,json,time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import fetch_selected_stdlib as downloader
import query_seranet_stdlib_v3 as prior

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
OUT=HERE/'primary_attempt02'

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    prior.base.own_priority(); prior.resource_guard()
    q=json.loads((HERE/'location_attempt01/receipt.json').read_text(encoding='utf-8'))
    r=next(r for r in q['records'] if r['key']=='seranet_openalex')
    assert r['complete']
    selected=[]
    for key,identity,title in [('seranet_candidate','W2963749200','Brain Segmentation from k-space with End-to-end Recurrent Attention Network'),
                               ('teacher_forcing','W3108772721','Multi-task MR Imaging with Iterative Teacher Forcing and Re-weighted Deep Learning')]:
        e=next(e for e in r['entries'] if e['id'].endswith('/'+identity))
        assert e['title']==title
        url=e['best_oa_location']['pdf_url']
        assert url in ('https://arxiv.org/pdf/1812.02068','https://arxiv.org/pdf/2011.13614')
        selected.append((key,e,url))
    OUT.mkdir(exist_ok=False); downloader.OUT=OUT
    start=time.perf_counter()
    with ThreadPoolExecutor(max_workers=2) as pool:
        rows=list(pool.map(downloader.fetch,selected))
    sys.path.insert(0,str(ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08/site_packages'))
    import pypdfium2 as pdfium
    for row in rows:
        if not row['complete']:continue
        src=ROOT/row['file']['path']
        doc=pdfium.PdfDocument(str(src))
        row['physical_pages']=len(doc); row['page_texts']=[]
        for n in range(len(doc)):
            prior.resource_guard()
            page=doc[n]; tp=page.get_textpage(); p=OUT/f"{row['key']}_page{n+1:03d}.txt"
            with p.open('x',encoding='utf-8') as f:f.write(tp.get_text_range())
            row['page_texts'].append(dict(physical_page=n+1,text_read=False,**prior.base.entry(p)))
            tp.close();page.close()
        doc.close()
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<30_000_000
    result=dict(complete=all(r['complete'] for r in rows),errors=[e for r in rows for e in r['errors']],records=rows,
        source_bindings=[prior.base.entry(p) for p in (Path(__file__),HERE/'RECURRENT_PRIMARY_SELECTION.md',HERE/'location_attempt01/receipt.json')],
        elapsed_seconds=time.perf_counter()-start,medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0)
    prior.base.new(OUT/'receipt.json',result)
    print(json.dumps(dict(complete=result['complete'],records=[{k:r.get(k) for k in ('key','complete','physical_pages','file','errors')} for r in rows])))
    return int(not result['complete'])

if __name__=='__main__':raise SystemExit(main())
