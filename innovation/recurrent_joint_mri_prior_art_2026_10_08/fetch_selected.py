"""Fetch only two actually indexed public MRI identities; extract without re-exporting."""
import sys,json,time,shutil,traceback
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
    index=HERE/'index_attempt01/receipt.json';q=json.loads(index.read_text(encoding='utf-8'))
    assert q['complete'] and not q['errors'];jobs=[]
    for key,ident,title in [
       ('mmar','2610.00553v1','Hetero-modal learning and corruption-resistant hetero-modal inference for joint segmentation of white matter hyperintensities and ischaemic stroke lesions in MRI'),
       ('xlstm_hved','2412.07804v3','XLSTM-HVED: Cross-Modal Brain Tumor Segmentation and MRI Reconstruction Method Using Vision XLSTM and Heteromodal Variational Encoder-Decoder')]:
        hits=[e for r in q['records'] for e in r['entries'] if e['id'].endswith('/'+ident)]
        assert len(hits)==1 and hits[0]['title']==title and hits[0]['authors'];jobs.append((key,hits[0]))
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
                row['page_texts'].append(dict(physical_page=n+1,text_read=False,**base.entry(p)));tp.close();page.close()
            doc.close()
        except Exception as e:row['complete']=False;row['errors'].append(type(e).__name__+': '+str(e));row['traceback']=traceback.format_exc()
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=all(r['complete'] for r in rows),
       errors=[e for r in rows for e in r['errors']],records=rows,source_bindings=[base.entry(p) for p in
       (Path(__file__),HERE/'PROTOCOL.md',HERE/'PRIMARY_SELECTION.md',index,
       ROOT/'task_adaptation_compute_prior_art_2026_10_08/query_primary.py',
       ROOT/'task_adaptation_compute_prior_art_2026_10_08/fetch_primary.py')],
       public_GET_only=True,TLS_verification_disabled=False,new_primary_papers_read=0,
       medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,new_agents_delegated=0,elapsed_seconds=time.perf_counter()-tick)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<30_000_000
    base.new(OUT/'receipt.json',result)
    print(json.dumps(dict(complete=result['complete'],records=[{k:r.get(k) for k in
       ('key','complete','download_complete','physical_pages','file','errors')} for r in rows]),ensure_ascii=False),flush=True)
    return int(not result['complete'])
if __name__=='__main__':raise SystemExit(main())

