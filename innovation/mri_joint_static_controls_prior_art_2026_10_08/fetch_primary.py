"""Bounded public PDF fetch for joint/frozen and static-control prior art."""
import json,sys,time,shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'task_adaptation_compute_prior_art_2026_10_08'))
import query_primary as base
import fetch_primary as previous
OUT=HERE/'primary_attempt01'
def main():
    sys.stdout.reconfigure(encoding='utf-8');base.own_priority()
    assert shutil.disk_usage(ROOT).free>8_050_000_000
    index=ROOT/'mri_decision_policy_prior_art_2026_10_08/index_attempt01/receipt.json'
    data=json.loads(index.read_text(encoding='utf-8'));assert data['complete']
    selections=[]
    for key,ident,title in [('masc','2602.00348v1','MASC: Metal-Aware Sampling and Correction via Reinforcement Learning for Accelerated MRI'),
        ('cartesian_thesis','2312.04327v1','Learning to sample in Cartesian MRI')]:
        hits=[e for r in data['records'] for e in r['entries'] if e['id'].endswith('/'+ident)]
        assert len(hits)==1 and hits[0]['title']==title and hits[0]['authors'];selections.append((key,hits[0]))
    OUT.mkdir(exist_ok=False);previous.OUT=OUT;tick=time.perf_counter()
    with ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(previous.fetch,selections))
    sys.path.insert(0,str(ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08/site_packages'))
    from pypdf import PdfReader
    for row in rows:
        if not row['complete']:continue
        reader=PdfReader(ROOT/row['file']['path']);row['physical_pages']=len(reader.pages);row['page_texts']=[]
        for n,page in enumerate(reader.pages,1):
            path=OUT/f"{row['key']}_page{n:03d}.txt"
            with path.open('x',encoding='utf-8') as f:f.write(page.extract_text() or '')
            row['page_texts'].append(dict(physical_page=n,text_read=False,**base.entry(path)))
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=all(r['complete'] for r in rows),errors=[],records=rows,
        source_bindings=[base.entry(Path(__file__)),base.entry(HERE/'PROTOCOL.md'),base.entry(index),
            base.entry(ROOT/'task_adaptation_compute_prior_art_2026_10_08/fetch_primary.py')],
        public_GET_only=True,TLS_verification_disabled=False,new_primary_papers_read=0,
        medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,training_updates=0,
        elapsed_seconds=time.perf_counter()-tick,goal_status='active')
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<30_000_000
    base.new(OUT/'receipt.json',result)
    print(json.dumps(dict(complete=result['complete'],records=[{k:r.get(k) for k in
        ('key','complete','physical_pages','file','errors')} for r in rows]),ensure_ascii=False),flush=True)
    return int(not result['complete'])
if __name__=='__main__':raise SystemExit(main())
