"""Obtain exactly two selected indexed versions; extraction is not reading."""
import json, subprocess, sys, traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
from query_acquisition_prior_art import entry

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
OUT=HERE/'primary_attempt01'

def fetch(selection):
    key, record, index = selection
    links=[v['href'] for v in record['links'] if v.get('type')=='application/pdf']
    assert len(links)==1
    url=links[0];assert urlsplit(url).netloc=='arxiv.org' and url.startswith('https://')
    row=dict(key=key,indexed_record=record,index_receipt=entry(index),requested_url=url,complete=False,errors=[])
    try:
        p=OUT/(key+'.pdf')
        proc=subprocess.run(['curl.exe','--noproxy','*','--fail','--silent','--show-error','--location',
            '--max-redirs','3','--proto','=https','--proto-redir','=https','--max-time','30',
            '--max-filesize','10000000','--dump-header',str(OUT/(key+'_headers.txt')),
            '--output',str(p),'--write-out','%{http_code}\n%{url_effective}',url],capture_output=True,timeout=35)
        (OUT/(key+'_stderr.txt')).write_bytes(proc.stderr)
        row.update(curl_exit=proc.returncode,status_and_effective_url=proc.stdout.decode('utf-8',errors='replace'))
        assert proc.returncode==0,proc.stderr.decode('utf-8',errors='replace')
        assert p.read_bytes().startswith(b'%PDF-') and p.stat().st_size<=10_000_000
        row.update(complete=True,file=entry(p))
    except Exception as exc:
        row['errors'].append(type(exc).__name__+': '+str(exc));row['traceback']=traceback.format_exc()
    return row

def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    source0=HERE/'index_attempt01/receipt.json';source1=HERE/'index_followup_attempt01/receipt.json'
    a=json.loads(source0.read_text(encoding='utf-8'));b=json.loads(source1.read_text(encoding='utf-8'))
    dyn=[e for r in a['records'] for e in r.get('entries',[]) if e.get('id','').endswith('/2503.01075v2')]
    tackle=[e for r in b['records'] for e in r.get('entries',[]) if e.get('id','').endswith('/2304.12507v3')]
    assert len(dyn)==len(tackle)==1
    with ThreadPoolExecutor(max_workers=2) as pool:
        rows=list(pool.map(fetch,[('dynamicdps',dyn[0],source0),('tackle',tackle[0],source1)]))
    sys.path.insert(0,str(ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08/site_packages'))
    from pypdf import PdfReader
    for row in rows:
        if row['complete']:
            try:
                reader=PdfReader(ROOT/row['file']['path']);row['physical_pages']=len(reader.pages);row['page_texts']=[]
                for i,page in enumerate(reader.pages,1):
                    p=OUT/(row['key']+'_page'+str(i).zfill(2)+'.txt')
                    with p.open('x',encoding='utf-8') as f:f.write(page.extract_text() or '')
                    row['page_texts'].append(dict(physical_page=i,text_read=False,**entry(p)))
            except Exception as e:row['complete']=False;row['errors'].append(type(e).__name__+': '+str(e))
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=all(v['complete'] for v in rows),records=rows,
        source_bindings=[entry(Path(__file__)),entry(HERE/'query_acquisition_prior_art.py'),entry(HERE/'PROTOCOL.md')],
        public_GET_only=True,TLS_verification_disabled=False,new_papers_read=0,
        medical_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,training_updates=0)
    with (OUT/'receipt.json').open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(dict(complete=r['complete'],records=[{k:v.get(k) for k in ('key','complete','physical_pages','errors','file')} for v in rows]),ensure_ascii=False),flush=True)
    return int(not r['complete'])

if __name__=='__main__':raise SystemExit(main())
