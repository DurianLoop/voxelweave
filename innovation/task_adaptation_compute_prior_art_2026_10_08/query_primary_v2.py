"""Attempt02: Python verified HTTPS after Windows schannel credentials failure."""
import json,sys,time,traceback,shutil,ssl
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request,urlopen
from urllib.parse import urlencode
import xml.etree.ElementTree as ET
from pathlib import Path
from query_primary import HERE,ROOT,entry,new,own_priority
OUT=HERE/'index_attempt02'

def fetch(job):
    key,provider,query=job;tick=time.perf_counter()
    args=dict(search_query=query,start=0,max_results=8) if provider=='arxiv' else {'query.title':query,'rows':8}
    url=('https://export.arxiv.org/api/query?' if provider=='arxiv' else 'https://api.crossref.org/works?')+urlencode(args)
    row=dict(key=key,provider=provider,query=query,requested_url=url,complete=False,errors=[])
    try:
        req=Request(url,headers={'User-Agent':'MRI-literature-audit/1.0'})
        with urlopen(req,timeout=30,context=ssl.create_default_context()) as response:
            payload=response.read(3_000_001);assert len(payload)<=3_000_000
            row.update(http_status=response.status,effective_url=response.url)
            with (OUT/(key+'_headers.txt')).open('x',encoding='utf-8') as f:f.write(str(response.headers))
        path=OUT/(key+('.xml' if provider=='arxiv' else '.json'))
        with path.open('xb') as f:f.write(payload)
        if provider=='arxiv':
            tree=ET.fromstring(payload);ns={'a':'http://www.w3.org/2005/Atom','o':'http://a9.com/-/spec/opensearch/1.1/'}
            row['total_results']=tree.findtext('o:totalResults',namespaces=ns)
            row['entries']=[dict(id=e.findtext('a:id',namespaces=ns),title=' '.join((e.findtext('a:title',namespaces=ns) or '').split()),
                published=e.findtext('a:published',namespaces=ns),updated=e.findtext('a:updated',namespaces=ns),
                authors=[a.findtext('a:name',namespaces=ns) for a in e.findall('a:author',ns)],summary=e.findtext('a:summary',namespaces=ns),
                links=[dict(v.attrib) for v in e.findall('a:link',ns)]) for e in tree.findall('a:entry',ns)]
        else:
            d=json.loads(payload);row['total_results']=d['message']['total-results']
            row['entries']=[{k:v.get(k) for k in ('title','DOI','author','published','abstract','link','URL')} for v in d['message']['items']]
        row.update(complete=True,file=entry(path))
    except Exception as e:row['errors'].append(type(e).__name__+': '+str(e));row['traceback']=traceback.format_exc()
    row['elapsed_seconds']=time.perf_counter()-tick;return row

def main():
    sys.stdout.reconfigure(encoding='utf-8');own_priority();assert shutil.disk_usage(ROOT).free>8_050_000_000
    OUT.mkdir(exist_ok=False)
    jobs=[('task_adapted','arxiv','ti:"Task adapted reconstruction for inverse problems"'),
          ('tuning_free','arxiv','ti:"Tuning-free Plug-and-Play"'),
          ('adaptive_mri','crossref','adaptive computation early exit magnetic resonance image reconstruction')]
    with ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(fetch,jobs))
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=all(r['complete'] for r in rows),records=rows,
        source_bindings=[entry(Path(__file__)),entry(HERE/'query_primary.py'),entry(HERE/'PROTOCOL.md'),entry(HERE/'index_attempt01/receipt.json')],
        public_GET_only=True,TLS_verification_disabled=False,new_papers_read=0,medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,training_updates=0)
    new(OUT/'receipt.json',result);print(json.dumps(result,ensure_ascii=False),flush=True)
    return int(not result['complete'])

if __name__=='__main__':raise SystemExit(main())
