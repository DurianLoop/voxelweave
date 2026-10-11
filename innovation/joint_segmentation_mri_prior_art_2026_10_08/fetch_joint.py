"""Download two verified index identities and extract with the existing PDFium package."""
import json,sys,time,shutil,traceback
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'primary_attempt01'
sys.path.insert(0,str(ROOT/'task_adaptation_compute_prior_art_2026_10_08'))
import query_primary as base
import fetch_primary as previous
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def main():
    sys.stdout.reconfigure(encoding='utf-8');base.own_priority();resource_guard()
    assert shutil.disk_usage(ROOT).free>8_050_000_000
    sources=[HERE/'index_attempt01/receipt.json',HERE/'index_followup_attempt01/receipt.json']
    data=[json.loads(p.read_text(encoding='utf-8')) for p in sources]
    assert all(q['complete'] and not q['errors'] for q in data)
    jobs=[]
    for key,ident,title in [
       ('segnetmri','1805.02165v1','Joint CS-MRI Reconstruction and Segmentation with a Unified Deep Network'),
       ('calibrationless','2105.09220v1','Joint Calibrationless Reconstruction and Segmentation of Parallel MRI')]:
        hits=[e for q in data for row in q['records'] for e in row.get('entries',[]) if e.get('id','').endswith('/'+ident)]
        assert hits and all(e['title']==title and e['authors'] for e in hits)
        assert all(e==hits[0] for e in hits);jobs.append((key,hits[0]))
    OUT.mkdir(exist_ok=False);previous.OUT=OUT;tick=time.perf_counter()
    with ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(previous.fetch,jobs))
    sys.path.insert(0,str(ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08/site_packages'))
    import pypdfium2 as pdfium
    for row in rows:
        row['download_complete']=row['complete']
        if not row['complete']:continue
        try:
            doc=pdfium.PdfDocument(str(ROOT/row['file']['path']));row['physical_pages']=len(doc);row['page_texts']=[]
            for n in range(len(doc)):
                resource_guard();page=doc[n];tp=page.get_textpage();s=tp.get_text_range()
                p=OUT/f"{row['key']}_page{n+1:03d}.txt"
                with p.open('x',encoding='utf-8') as f:f.write(s)
                row['page_texts'].append(dict(physical_page=n+1,text_read=False,**base.entry(p)))
                tp.close();page.close()
            doc.close();row['extractor']='existing pypdfium2'
        except Exception as e:row['complete']=False;row['errors'].append(type(e).__name__+': '+str(e));row['extraction_traceback']=traceback.format_exc()
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=all(r['complete'] for r in rows),
       errors=[e for r in rows for e in r['errors']],records=rows,source_bindings=[base.entry(p) for p in
       (Path(__file__),HERE/'PROTOCOL.md',HERE/'PRIMARY_SELECTION.md',*sources,
       ROOT/'task_adaptation_compute_prior_art_2026_10_08/query_primary.py',
       ROOT/'task_adaptation_compute_prior_art_2026_10_08/fetch_primary.py')],
       public_GET_only=True,TLS_verification_disabled=False,new_primary_papers_read=0,
       medical_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,
       new_agents_delegated=0,elapsed_seconds=time.perf_counter()-tick)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<30_000_000
    base.new(OUT/'receipt.json',result)
    print(json.dumps(dict(complete=result['complete'],records=[{k:r.get(k) for k in
       ('key','complete','download_complete','physical_pages','file','errors')} for r in rows]),ensure_ascii=False),flush=True)
    return int(not result['complete'])
if __name__=='__main__':raise SystemExit(main())

