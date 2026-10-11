"""Fetch two previously screened identities; no repeated index queries."""
import json,sys,time,shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent; OUT=HERE/'primary_attempt01'
sys.path.insert(0,str(ROOT/'task_adaptation_compute_prior_art_2026_10_08'))
import query_primary as base
import fetch_primary as previous

def main():
    sys.stdout.reconfigure(encoding='utf-8'); base.own_priority()
    assert shutil.disk_usage(ROOT).free>8_050_000_000
    index=ROOT/'mri_decision_policy_prior_art_2026_10_08/index_attempt01/receipt.json'
    q=json.loads(index.read_text(encoding='utf-8')); assert q['complete'] and not q['errors']
    items=[]
    for key,ident,title in [('tadt','2408.08736v2','Task-Aware Dynamic Transformer for Efficient Arbitrary-Scale Image Super-Resolution'),
        ('medical_shift','2604.10904v1','Evaluating the Impact of Medical Image Reconstruction on Downstream AI Fairness and Performance')]:
        hits=[e for r in q['records'] for e in r['entries'] if e['id'].endswith('/'+ident)]
        assert len(hits)==1 and hits[0]['title']==title and hits[0]['authors']; items.append((key,hits[0]))
    OUT.mkdir(exist_ok=False); previous.OUT=OUT; start=time.perf_counter()
    with ThreadPoolExecutor(max_workers=2) as pool: records=list(pool.map(previous.fetch,items))
    sys.path.insert(0,str(ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08/site_packages'))
    from pypdf import PdfReader
    for row in records:
        if not row['complete']: continue
        reader=PdfReader(ROOT/row['file']['path']); row['physical_pages']=len(reader.pages); row['page_texts']=[]
        for i,page in enumerate(reader.pages,1):
            p=OUT/f"{row['key']}_page{i:03d}.txt"
            with p.open('x',encoding='utf-8') as f:f.write(page.extract_text() or '')
            row['page_texts'].append(dict(physical_page=i,text_read=False,**base.entry(p)))
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=all(r['complete'] for r in records),errors=[],records=records,
        source_bindings=[base.entry(p) for p in (Path(__file__),HERE/'PROTOCOL.md',index,
          ROOT/'task_adaptation_compute_prior_art_2026_10_08/query_primary.py',ROOT/'task_adaptation_compute_prior_art_2026_10_08/fetch_primary.py')],
        public_GET_only=True,TLS_verification_disabled=False,network_index_requests=0,new_papers_read=0,
        medical_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,training_updates=0,elapsed_seconds=time.perf_counter()-start)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<30_000_000
    base.new(OUT/'receipt.json',result)
    print(json.dumps(dict(complete=result['complete'],records=[{k:r.get(k) for k in ('key','complete','physical_pages','file','errors')} for r in records]),ensure_ascii=False),flush=True)
    return 0 if result['complete'] else 1
if __name__=='__main__':raise SystemExit(main())
