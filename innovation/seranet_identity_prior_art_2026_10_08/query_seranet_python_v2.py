"""Same planned GETs using verified Python HTTPS after Windows Schannel failed."""
import sys,json,time,shutil,traceback,xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import urlencode,urlsplit
from concurrent.futures import ThreadPoolExecutor
import requests
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'index_attempt02'
sys.path.insert(0,str(ROOT/'task_adaptation_compute_prior_art_2026_10_08'))
import query_primary as base
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def fetch(job):
    key,provider,query=job;tick=time.perf_counter()
    args=dict(search_query=query,start=0,max_results=8) if provider=='arxiv' else {'query.title':query,'rows':8}
    url=('https://export.arxiv.org/api/query?' if provider=='arxiv' else 'https://api.crossref.org/works?')+urlencode(args)
    row=dict(key=key,provider=provider,query=query,requested_url=url,complete=False,errors=[])
    try:
        with requests.Session() as session:
            session.trust_env=False;session.max_redirects=3
            with session.get(url,timeout=30,stream=True,verify=True) as response:
                row.update(HTTP_status=response.status_code,effective_url=response.url,
                    redirects=[dict(status=r.status_code,url=r.url) for r in response.history])
                assert all(urlsplit(u).scheme=='https' for u in [url,response.url]+[r.url for r in response.history])
                base.new(OUT/(key+'_headers.json'),dict(status=response.status_code,headers=dict(response.headers)))
                response.raise_for_status();chunks=[];total=0
                for block in response.iter_content(65536):
                    total+=len(block);assert total<=3_000_000,'Bounded public response exceeded 3MB'
                    assert time.perf_counter()-tick<=35,'Bounded wall time exceeded'
                    chunks.append(block)
                body=b''.join(chunks)
        dest=OUT/(key+('.xml' if provider=='arxiv' else '.json'))
        with dest.open('xb') as f:f.write(body)
        if provider=='arxiv':
            tree=ET.fromstring(body);ns={'a':'http://www.w3.org/2005/Atom','o':'http://a9.com/-/spec/opensearch/1.1/'}
            row['total_results']=tree.findtext('o:totalResults',namespaces=ns)
            row['entries']=[dict(id=e.findtext('a:id',namespaces=ns),title=' '.join((e.findtext('a:title',namespaces=ns) or '').split()),
                published=e.findtext('a:published',namespaces=ns),updated=e.findtext('a:updated',namespaces=ns),
                authors=[a.findtext('a:name',namespaces=ns) for a in e.findall('a:author',ns)],
                summary=e.findtext('a:summary',namespaces=ns),links=[dict(v.attrib) for v in e.findall('a:link',ns)])
                for e in tree.findall('a:entry',ns)]
        else:
            payload=json.loads(body);row['total_results']=payload['message']['total-results']
            row['entries']=[{k:v.get(k) for k in ['title','DOI','author','published','abstract','link','URL']} for v in payload['message']['items']]
        row.update(complete=True,file=base.entry(dest))
    except Exception as e:row['errors'].append(type(e).__name__+': '+str(e));row['traceback']=traceback.format_exc()
    row['elapsed_seconds']=time.perf_counter()-tick;return row
def main():
    sys.stdout.reconfigure(encoding='utf-8');base.own_priority();resource_guard()
    assert shutil.disk_usage(ROOT).free>8_050_000_000;OUT.mkdir(exist_ok=False);tick=time.perf_counter()
    jobs=[('seranet_crossref','crossref','SERANet'),('segmentation_aware_crossref','crossref','Segmentation-aware MRI reconstruction'),
        ('segmentation_aware_arxiv','arxiv','all:"segmentation-aware" AND (all:MRI OR all:"magnetic resonance") AND submittedDate:[199101010000 TO 202610082359]')]
    with ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(fetch,jobs))
    q=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=all(r['complete'] for r in rows),
        errors=[e for r in rows for e in r['errors']],records=rows,source_bindings=[base.entry(p) for p in
        (Path(__file__),HERE/'PROTOCOL.md',HERE/'HTTPS_REPAIR.md',HERE/'index_attempt01/receipt.json')],
        public_GET_only=True,TLS_verification_disabled=False,authentication_used=False,automatic_retries=False,
        new_primary_papers_read=0,medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,new_agents_delegated=0,
        resource_snapshot=resource_guard(),elapsed_seconds=time.perf_counter()-tick)
    base.new(OUT/'receipt.json',q)
    print(json.dumps(dict(complete=q['complete'],errors=q['errors'],records=[dict(key=r['key'],complete=r['complete'],
        total_results=r.get('total_results'),entries=r.get('entries',[]),errors=r['errors']) for r in rows]),ensure_ascii=False),flush=True)
    return int(not q['complete'])
if __name__=='__main__':raise SystemExit(main())
