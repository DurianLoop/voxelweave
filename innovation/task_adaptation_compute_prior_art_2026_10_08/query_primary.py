"""Three bounded public index requests, preserving every returned title and failure."""
import hashlib,json,subprocess,sys,time,traceback,ctypes,shutil
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlencode
import xml.etree.ElementTree as ET

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
OUT=HERE/'index_attempt01'

def entry(p):
    return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())

def new(p,v):
    with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')

def own_priority():
    k=ctypes.WinDLL('kernel32',use_last_error=True);k.GetCurrentProcess.restype=ctypes.c_void_p
    k.SetPriorityClass.argtypes=(ctypes.c_void_p,ctypes.c_uint32)
    assert k.SetPriorityClass(k.GetCurrentProcess(),0x00004000)

def fetch(job):
    key,provider,query=job;tick=time.perf_counter()
    args=dict(search_query=query,start=0,max_results=8) if provider=='arxiv' else {'query.title':query,'rows':8}
    url=('https://export.arxiv.org/api/query?' if provider=='arxiv' else 'https://api.crossref.org/works?')+urlencode(args)
    row=dict(key=key,provider=provider,query=query,requested_url=url,complete=False,errors=[])
    try:
        path=OUT/(key+('.xml' if provider=='arxiv' else '.json'))
        assert not path.exists()
        r=subprocess.run(['curl.exe','--noproxy','*','--fail','--silent','--show-error','--location',
            '--max-redirs','3','--proto','=https','--proto-redir','=https','--max-time','30','--max-filesize','3000000',
            '--dump-header',str(OUT/(key+'_headers.txt')),'--output',str(path),'--write-out','%{http_code}\n%{url_effective}',url],
            capture_output=True,timeout=35)
        (OUT/(key+'_stderr.txt')).write_bytes(r.stderr)
        row.update(curl_exit=r.returncode,status_and_effective_url=r.stdout.decode('utf-8',errors='replace'))
        assert r.returncode==0,r.stderr.decode('utf-8',errors='replace')
        if provider=='arxiv':
            tree=ET.fromstring(path.read_bytes());ns={'a':'http://www.w3.org/2005/Atom','o':'http://a9.com/-/spec/opensearch/1.1/'}
            row['total_results']=tree.findtext('o:totalResults',namespaces=ns)
            row['entries']=[dict(id=e.findtext('a:id',namespaces=ns),title=' '.join((e.findtext('a:title',namespaces=ns) or '').split()),
                published=e.findtext('a:published',namespaces=ns),updated=e.findtext('a:updated',namespaces=ns),
                authors=[a.findtext('a:name',namespaces=ns) for a in e.findall('a:author',ns)],
                summary=e.findtext('a:summary',namespaces=ns),links=[dict(v.attrib) for v in e.findall('a:link',ns)])
                for e in tree.findall('a:entry',ns)]
        else:
            d=json.loads(path.read_text(encoding='utf-8'));row['total_results']=d['message']['total-results']
            row['entries']=[{k:v.get(k) for k in ('title','DOI','author','published','abstract','link','URL')} for v in d['message']['items']]
        row.update(complete=True,file=entry(path))
    except Exception as e:row['errors'].append(type(e).__name__+': '+str(e));row['traceback']=traceback.format_exc()
    row['elapsed_seconds']=time.perf_counter()-tick
    return row

def main():
    sys.stdout.reconfigure(encoding='utf-8');own_priority()
    free=shutil.disk_usage(ROOT).free;assert free>8_050_000_000
    OUT.mkdir(exist_ok=False)
    jobs=[('task_adapted','arxiv','ti:"Task adapted reconstruction for inverse problems"'),
          ('tuning_free','arxiv','ti:"Tuning-free Plug-and-Play"'),
          ('adaptive_mri','crossref','adaptive computation early exit magnetic resonance image reconstruction')]
    with ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(fetch,jobs))
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=all(r['complete'] for r in rows),records=rows,
        source_bindings=[entry(Path(__file__)),entry(HERE/'PROTOCOL.md')],public_GET_only=True,TLS_verification_disabled=False,
        workspace_free_bytes=free,new_papers_read=0,medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,training_updates=0)
    new(OUT/'receipt.json',result)
    print(json.dumps(result,ensure_ascii=False),flush=True)
    return int(not result['complete'])

if __name__=='__main__':raise SystemExit(main())
