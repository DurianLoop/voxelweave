"""Read the actual earlier index and fetch its MIRTO PDF; extraction is not reading."""
import sys,json,time,traceback
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'primary_attempt01'
sys.path.insert(0,str(ROOT/'seranet_identity_prior_art_2026_10_08'))
import fetch_selected_stdlib as downloader
client=downloader.prior;base=client.base

def main():
    sys.stdout.reconfigure(encoding='utf-8');client.resource_guard()
    index=ROOT/'adaptive_compute_task_budget_prior_art_2026_10_08/index_attempt01/receipt.json'
    q=json.loads(index.read_text(encoding='utf-8'));assert q['complete']
    r=next(e for r in q['records'] for e in r['entries'] if e['id'].endswith('/2610.02136v1'))
    urls=[l['href'] for l in r['links'] if l.get('type')=='application/pdf'];assert urls==['https://arxiv.org/pdf/2610.02136v1']
    OUT.mkdir(exist_ok=False);downloader.OUT=OUT;tick=time.perf_counter();record=downloader.fetch(('mirto',r,urls[0]))
    if record['complete']:
        try:
            sys.path.insert(0,str(ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08/site_packages'))
            import pypdfium2 as pdfium
            doc=pdfium.PdfDocument(str(ROOT/record['file']['path']));record['physical_pages']=len(doc);record['page_texts']=[]
            for n in range(len(doc)):
                client.resource_guard();page=doc[n];tp=page.get_textpage();p=OUT/f'mirto_page{n+1:03d}.txt'
                with p.open('x',encoding='utf-8') as f:f.write(tp.get_text_range())
                record['page_texts'].append(dict(physical_page=n+1,text_read=False,**base.entry(p)))
                tp.close();page.close()
            doc.close()
        except Exception as e:record['complete']=False;record['errors'].append(repr(e));record['traceback']=traceback.format_exc()
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=record['complete'],errors=record['errors'],records=[record],
        source_bindings=[base.entry(p) for p in (Path(__file__),HERE/'PROTOCOL.md',HERE/'PRIMARY_SELECTION.md',index)],
        resource_snapshot=client.resource_guard(),elapsed_seconds=time.perf_counter()-tick,new_primary_papers_read=0,
        medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,new_agents_delegated=0)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<30_000_000
    base.new(OUT/'receipt.json',result)
    print(json.dumps({k:record.get(k) for k in ('key','complete','HTTP_status','physical_pages','file','errors')},ensure_ascii=False),flush=True)
    return int(not result['complete'])
if __name__=='__main__':raise SystemExit(main())
