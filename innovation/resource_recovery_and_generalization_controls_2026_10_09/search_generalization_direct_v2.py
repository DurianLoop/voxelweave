"""Same three public queries once over the previously used verified-TLS direct transport."""
import json,ssl,sys,time,urllib.request,urllib.parse
from pathlib import Path
from search_generalization_sources import QUERIES
from inventory_frozen_text_storage import HERE,entry,dump,guard

def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();before=guard(started)
    out=HERE/'public_index_attempt02';out.mkdir(exist_ok=False)
    dump(out/'frozen_queries.json',dict(queries=QUERIES,pageSize=8,max_response_bytes=400_000,
        source_bindings=[entry(Path(__file__)),entry(HERE/'search_generalization_sources.py'),
                         entry(HERE/'PUBLIC_DIRECT_TRANSPORT_ATTEMPT02.md')]))
    context=ssl.create_default_context();assert context.check_hostname and context.verify_mode==ssl.CERT_REQUIRED
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=context))
    rows=[]
    for i,query in enumerate(QUERIES,1):
        guard(started)
        url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode(dict(query=query,format='json',pageSize=8,resultType='core'))
        row=dict(query=query,requested_url=url,complete=False)
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'MRIResearchLiterature/1.0','Accept':'application/json'})
            with opener.open(req,timeout=25) as resp:
                body=resp.read(400_001);assert len(body)<=400_000
                row.update(http_status=resp.status,effective_url=resp.url)
            path=out/f'query{i}.json'
            with path.open('xb') as f:f.write(body)
            data=json.loads(body)
            row.update(complete=True,hitCount=data['hitCount'],raw_response=entry(path),items=[])
            for hit in data['resultList']['result']:
                row['items'].append({key:hit.get(key) for key in ['id','source','pmcid','doi','title','authorString','pubYear','firstPublicationDate','isOpenAccess','abstractText']})
        except Exception as exc:row['error']=dict(type=type(exc).__name__,message=str(exc))
        rows.append(row)
        print(json.dumps(row,ensure_ascii=False),flush=True)
    result=dict(complete=all(row['complete'] for row in rows),queries=rows,resources_before=before,
        resources_after=guard(started),elapsed_seconds=time.perf_counter()-started,
        new_maintexts_read=0,patient_information_uploaded=False,goal_status='active')
    dump(out/'receipt.json',result);return int(not result['complete'])

if __name__=='__main__':raise SystemExit(main())
