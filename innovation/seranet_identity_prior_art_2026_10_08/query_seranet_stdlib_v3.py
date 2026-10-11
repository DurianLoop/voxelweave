"""Verified standard-library HTTPS; neither Schannel nor an uninstalled requests package."""
import sys,json,time,shutil,traceback,ssl,xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import urlencode,urlsplit
from urllib.request import build_opener,HTTPSHandler,HTTPRedirectHandler,ProxyHandler,Request
from concurrent.futures import ThreadPoolExecutor
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'index_attempt03'
sys.path.insert(0,str(ROOT/'task_adaptation_compute_prior_art_2026_10_08'))
import query_primary as base
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
class LimitedRedirect(HTTPRedirectHandler):
    max_redirections=3
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        assert urlsplit(newurl).scheme=='https','Only verified HTTPS redirects permitted'
        return super().redirect_request(req,fp,code,msg,headers,newurl)
def fetch(job):
    key,provider,query=job;tick=time.perf_counter()
    args=dict(search_query=query,start=0,max_results=8) if provider=='arxiv' else {'query.title':query,'rows':8}
    url=('https://export.arxiv.org/api/query?' if provider=='arxiv' else 'https://api.crossref.org/works?')+urlencode(args)
    row=dict(key=key,provider=provider,query=query,requested_url=url,complete=False,errors=[])
    try:
        context=ssl.create_default_context()
        assert context.verify_mode==ssl.CERT_REQUIRED and context.check_hostname
        opener=build_opener(ProxyHandler({}),HTTPSHandler(context=context),LimitedRedirect())
        req=Request(url,headers={'User-Agent':'MRI-innovation-literature-audit/1.0'},method='GET')
        with opener.open(req,timeout=30) as response:
            row.update(HTTP_status=response.status,effective_url=response.geturl())
            assert urlsplit(response.geturl()).scheme=='https'
            base.new(OUT/(key+'_headers.json'),dict(status=response.status,headers=dict(response.headers)))
            chunks=[];total=0
            while True:
                block=response.read(65536)
                if not block:break
                total+=len(block);assert total<=3_000_000,'Public response exceeded 3MB'
                assert time.perf_counter()-tick<=35,'Bounded request wall time exceeded'
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
        (Path(__file__),HERE/'PROTOCOL.md',HERE/'HTTPS_REPAIR.md',HERE/'HTTPS_REPAIR_V3.md',
         HERE/'query_seranet_python_v2.py',HERE/'index_attempt01/receipt.json')],
        public_GET_only=True,TLS_verification_disabled=False,authentication_used=False,automatic_retries=False,
        new_primary_papers_read=0,medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,new_agents_delegated=0,
        resource_snapshot=resource_guard(),elapsed_seconds=time.perf_counter()-tick)
    base.new(OUT/'receipt.json',q)
    print(json.dumps(dict(complete=q['complete'],errors=q['errors'],records=[dict(key=r['key'],complete=r['complete'],
        total_results=r.get('total_results'),entries=r.get('entries',[]),errors=r['errors']) for r in rows]),ensure_ascii=False),flush=True)
    return int(not q['complete'])
if __name__=='__main__':raise SystemExit(main())
