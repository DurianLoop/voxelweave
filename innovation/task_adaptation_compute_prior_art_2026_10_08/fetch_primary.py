"""Fetch two identity-checked indexed versions; extraction is not reading."""
import json,subprocess,sys,traceback,time,shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import urlsplit
from query_primary import HERE,ROOT,entry,new,own_priority
OUT=HERE/'primary_attempt01'

def fetch(item):
    key,record=item;row=dict(key=key,indexed_record=record,complete=False,errors=[])
    try:
        urls=[v['href'] for v in record['links'] if v.get('type')=='application/pdf'];assert len(urls)==1
        url=urls[0];assert url.startswith('https://') and urlsplit(url).netloc=='arxiv.org';row['requested_url']=url
        p=OUT/(key+'.pdf');assert not p.exists()
        r=subprocess.run(['curl.exe','--noproxy','*','--fail','--silent','--show-error','--location',
            '--max-redirs','3','--proto','=https','--proto-redir','=https','--max-time','30','--max-filesize','10000000',
            '--dump-header',str(OUT/(key+'_headers.txt')),'--output',str(p),'--write-out','%{http_code}\n%{url_effective}',url],
            capture_output=True,timeout=35)
        (OUT/(key+'_stderr.txt')).write_bytes(r.stderr)
        row.update(curl_exit=r.returncode,status_and_effective_url=r.stdout.decode('utf-8',errors='replace'))
        assert r.returncode==0,r.stderr.decode('utf-8',errors='replace')
        assert p.read_bytes().startswith(b'%PDF-');row.update(complete=True,file=entry(p))
    except Exception as e:row['errors'].append(type(e).__name__+': '+str(e));row['traceback']=traceback.format_exc()
    return row

def main():
    sys.stdout.reconfigure(encoding='utf-8');own_priority();assert shutil.disk_usage(ROOT).free>8_050_000_000
    OUT.mkdir(exist_ok=False);index=HERE/'index_attempt03/receipt.json';data=json.loads(index.read_text(encoding='utf-8'))
    selections=[]
    for key,identifier,title in [('task_adapted','1809.00948v1','Task adapted reconstruction for inverse problems'),
            ('tuning_free','2002.09611v2','Tuning-free Plug-and-Play Proximal Algorithm for Inverse Imaging Problems')]:
        hits=[e for r in data['records'] for e in r.get('entries',[]) if e.get('id','').endswith('/'+identifier)]
        assert len(hits)==1 and hits[0]['title']==title and hits[0]['authors']
        selections.append((key,hits[0]))
    tick=time.perf_counter()
    with ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(fetch,selections))
    sys.path.insert(0,str(ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08/site_packages'))
    from pypdf import PdfReader
    for row in rows:
        if row['complete']:
            try:
                reader=PdfReader(ROOT/row['file']['path']);row['physical_pages']=len(reader.pages);row['page_texts']=[]
                for i,page in enumerate(reader.pages,1):
                    textfile=OUT/(row['key']+'_page'+str(i).zfill(2)+'.txt')
                    with textfile.open('x',encoding='utf-8') as f:f.write(page.extract_text() or '')
                    row['page_texts'].append(dict(physical_page=i,text_read=False,**entry(textfile)))
            except Exception as e:row['complete']=False;row['errors'].append(type(e).__name__+': '+str(e))
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=all(r['complete'] for r in rows),records=rows,
        source_bindings=[entry(Path(__file__)),entry(HERE/'query_primary.py'),entry(HERE/'query_primary_v3.py'),entry(HERE/'PROTOCOL.md'),entry(index)],
        public_GET_only=True,TLS_verification_disabled=False,new_papers_read=0,elapsed_seconds=time.perf_counter()-tick,
        medical_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,training_updates=0)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<30_000_000
    new(OUT/'receipt.json',result)
    print(json.dumps(dict(complete=result['complete'],records=[{k:r.get(k) for k in ('key','complete','physical_pages','file','errors')} for r in rows]),ensure_ascii=False),flush=True)
    return int(not result['complete'])

if __name__=='__main__':raise SystemExit(main())
