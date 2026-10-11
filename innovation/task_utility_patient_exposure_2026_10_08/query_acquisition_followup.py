import json, subprocess, sys, time, traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from urllib.parse import urlencode
from pathlib import Path
import query_acquisition_prior_art as base

HERE = Path(__file__).resolve().parent
OUT = HERE / 'index_followup_attempt01'

def crossref():
    row = dict(key='task_aware_crossref', complete=False, errors=[])
    url = 'https://api.crossref.org/works?' + urlencode({'query.title':'task aware MRI acquisition TACKLE', 'rows':8})
    row['requested_url'] = url
    try:
        p = OUT/'task_aware_crossref.json'
        r = subprocess.run(['curl.exe','--noproxy','*','--fail','--silent','--show-error','--location',
            '--max-redirs','3','--proto','=https','--proto-redir','=https','--max-time','30',
            '--max-filesize','3000000','--dump-header',str(OUT/'crossref_headers.txt'),
            '--output',str(p),'--write-out','%{http_code}\n%{url_effective}',url], capture_output=True,timeout=35)
        (OUT/'crossref_stderr.txt').write_bytes(r.stderr)
        row.update(curl_exit=r.returncode,status_and_effective_url=r.stdout.decode('utf-8',errors='replace'))
        assert r.returncode==0,r.stderr.decode('utf-8',errors='replace')
        d=json.loads(p.read_text(encoding='utf-8'))
        row['total_results']=d['message']['total-results']
        row['entries']=[{k:v.get(k) for k in ('title','DOI','author','published','link','URL','abstract')} for v in d['message']['items']]
        row.update(complete=True,file=base.entry(p))
    except Exception as e:
        row['errors'].append(type(e).__name__+': '+str(e));row['traceback']=traceback.format_exc()
    return row

def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);base.OUT=OUT
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures=[pool.submit(base.fetch,('pineda','au:Pineda AND (all:MRI OR all:"magnetic resonance")')),
                 pool.submit(base.fetch,('tackle_all','all:TACKLE AND (all:MRI OR all:"magnetic resonance")')),
                 pool.submit(crossref)]
        rows=[f.result() for f in futures]
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=all(v['complete'] for v in rows),records=rows,
        source_bindings=[base.entry(Path(__file__)),base.entry(HERE/'query_acquisition_prior_art.py'),base.entry(HERE/'INDEX_FOLLOWUP.md'),
                         base.entry(HERE/'index_attempt01/receipt.json')],public_GET_only=True,TLS_verification_disabled=False,
        new_papers_read=0,medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,training_updates=0)
    with (OUT/'receipt.json').open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(r,ensure_ascii=False),flush=True)
    return int(not r['complete'])

if __name__=='__main__':raise SystemExit(main())
