"""Bounded bibliographic complement; EuropePMC zero hits cannot certify novelty."""
import sys,time,ssl,gzip,json,urllib.request,urllib.parse
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import resource_guard,entry,dump
QUERIES=['adaptive magnetic resonance imaging sampling reinforcement learning','task driven magnetic resonance image reconstruction segmentation']
started=time.perf_counter();before=resource_guard();assert before['workspace_free_bytes']-18_800_000>=8_000_000_000
out=HERE/'crossref_index_attempt01';out.mkdir(exist_ok=False)
dump(out/'frozen_queries.json',dict(queries=QUERIES,rows=6,maintext_read=False,source_bindings=[entry(Path(__file__)),entry(HERE/'PROTOCOL.md')]))
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ssl.create_default_context()));records=[]
for i,q in enumerate(QUERIES):
    url='https://api.crossref.org/works?'+urllib.parse.urlencode({'query.bibliographic':q,'rows':6,'select':'DOI,title,published,URL,abstract,link'})
    row=dict(query=q,requested_url=url,complete=False)
    try:
        with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRIResearchLiterature/1.0'}),timeout=25) as response:
            data=response.read(400_001);assert len(data)<=400_000;row.update(http_status=response.status,effective_url=response.url)
        p=out/f'query{i}.json.gz';p.write_bytes(gzip.compress(data,mtime=0));v=json.loads(data)
        row.update(complete=True,saved=entry(p),items=v['message']['items'])
    except Exception as e:row['error']=dict(type=type(e).__name__,message=str(e))
    records.append(row);print(json.dumps(dict(index=i,complete=row['complete'],error=row.get('error'),items=[{k:x.get(k) for k in ['DOI','title','link']} for x in row.get('items',[])])),flush=True)
    resource_guard();assert time.perf_counter()-started<120
result=dict(complete=all(r['complete'] for r in records),queries=records,new_maintexts_read=0,patient_information_uploaded=False,
    source_bindings=[entry(Path(__file__)),entry(HERE/'PROTOCOL.md')],resources_before=before,resources_after=resource_guard(),elapsed_seconds=time.perf_counter()-started,goal_status='active')
dump(out/'receipt.json',result);raise SystemExit(int(not result['complete']))
