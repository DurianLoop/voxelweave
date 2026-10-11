"""Three focused, bounded arXiv queries; preserve actual order and complete metadata."""
import sys,json,time,ssl,traceback
from datetime import datetime,timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.request import build_opener,ProxyHandler,HTTPSHandler,Request
from urllib.parse import urlencode
import xml.etree.ElementTree as ET
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'index_attempt01'
sys.path.insert(0,str(ROOT/'seranet_identity_prior_art_2026_10_08'))
import query_seranet_stdlib_v3 as client

def fetch(job):
    key,query=job;tick=time.perf_counter()
    query+=' AND submittedDate:[199101010000 TO 202610082359]'
    args=dict(search_query=query,start=0,max_results=8,sortBy='submittedDate',sortOrder='descending')
    url='https://export.arxiv.org/api/query?'+urlencode(args)
    row=dict(key=key,query=query,requested_url=url,complete=False,errors=[])
    try:
        context=ssl.create_default_context()
        opener=build_opener(ProxyHandler({}),HTTPSHandler(context=context),client.LimitedRedirect())
        req=Request(url,headers={'User-Agent':'MRI-innovation-literature-audit/1.0'})
        with opener.open(req,timeout=30) as response:
            row.update(HTTP_status=response.status,effective_url=response.geturl())
            client.base.new(OUT/(key+'_headers.json'),dict(status=response.status,headers=dict(response.headers)))
            blocks,total=[],0
            while True:
                b=response.read(65536)
                if not b:break
                total+=len(b);assert total<=3_000_000 and time.perf_counter()-tick<=35
                blocks.append(b)
            body=b''.join(blocks)
        p=OUT/(key+'.xml')
        with p.open('xb') as f:f.write(body)
        tree=ET.fromstring(body);ns={'a':'http://www.w3.org/2005/Atom','o':'http://a9.com/-/spec/opensearch/1.1/'}
        row['total_results']=tree.findtext('o:totalResults',namespaces=ns)
        row['entries']=[dict(id=e.findtext('a:id',namespaces=ns),title=' '.join((e.findtext('a:title',namespaces=ns) or '').split()),
            published=e.findtext('a:published',namespaces=ns),updated=e.findtext('a:updated',namespaces=ns),
            authors=[a.findtext('a:name',namespaces=ns) for a in e.findall('a:author',ns)],
            summary=e.findtext('a:summary',namespaces=ns),links=[dict(v.attrib) for v in e.findall('a:link',ns)]) for e in tree.findall('a:entry',ns)]
        row.update(complete=True,response_binding=client.base.entry(p))
    except Exception as e:
        row['errors'].append(type(e).__name__+': '+str(e));row['traceback']=traceback.format_exc()
    row['elapsed_seconds']=time.perf_counter()-tick
    return row

def main():
    sys.stdout.reconfigure(encoding='utf-8');client.base.own_priority();client.resource_guard()
    OUT.mkdir(exist_ok=False)
    jobs=[('mri_compute_stopping','(all:MRI OR all:"magnetic resonance") AND (all:"early exit" OR all:"adaptive computation" OR all:"learn to stop")'),
          ('mri_value','(all:MRI OR all:"magnetic resonance") AND (all:"value of information" OR all:"value of computation" OR all:"task utility")'),
          ('mri_budget','(ti:MRI OR ti:"magnetic resonance") AND (all:budget OR all:compute OR all:"adaptive stopping")')]
    with ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(fetch,jobs))
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=all(r['complete'] for r in rows),
        errors=[e for r in rows for e in r['errors']],records=rows,source_bindings=[client.base.entry(p) for p in (Path(__file__),HERE/'PROTOCOL.md')],
        sort_by='submittedDate',sort_order='descending',maximum_results_per_query=8,cutoff='2026-10-08',
        resource_snapshot=client.resource_guard(),public_GET_only=True,TLS_verification_disabled=False,
        medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,new_agents_delegated=0)
    client.base.new(OUT/'receipt.json',result)
    for r in rows:print(json.dumps({k:r.get(k) for k in ('key','complete','total_results','entries','errors')},ensure_ascii=False),flush=True)
    return int(not result['complete'])
if __name__=='__main__':raise SystemExit(main())
