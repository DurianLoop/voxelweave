"""Five bounded public prior-art searches; downloaded indices do not count as read maintexts."""
import sys,time,ssl,json,gzip,urllib.request,urllib.parse
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import resource_guard,entry,dump
MRI='(TITLE_ABS:MRI OR TITLE_ABS:"magnetic resonance")'
QUERIES=[
 MRI+' AND (TITLE_ABS:"adaptive acquisition" OR TITLE_ABS:"active acquisition" OR TITLE_ABS:"adaptive sampling") AND (TITLE_ABS:diagnostic OR TITLE_ABS:task OR TITLE_ABS:uncertainty) AND OPEN_ACCESS:Y',
 MRI+' AND (TITLE_ABS:"task-driven" OR TITLE_ABS:"task-aware" OR TITLE_ABS:"task-based") AND (TITLE_ABS:reconstruction OR TITLE_ABS:"super-resolution") AND OPEN_ACCESS:Y',
 '(TITLE_ABS:medical OR '+MRI+') AND (TITLE_ABS:"learning to defer" OR TITLE_ABS:"selective prediction" OR TITLE_ABS:"value of information") AND OPEN_ACCESS:Y',
 MRI+' AND (TITLE_ABS:"model selection" OR TITLE_ABS:routing OR TITLE_ABS:"mixture of experts") AND (TITLE_ABS:acquisition OR TITLE_ABS:reconstruction OR TITLE_ABS:segmentation) AND OPEN_ACCESS:Y',
 MRI+' AND (TITLE_ABS:reacquisition OR TITLE_ABS:"scan time" OR TITLE_ABS:budget) AND (TITLE_ABS:uncertainty OR TITLE_ABS:"reinforcement learning" OR TITLE_ABS:"decision making") AND OPEN_ACCESS:Y']
def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter()
    def guard():
        r=resource_guard();assert time.perf_counter()-started<300 and r['workspace_free_bytes']-18_800_000>=8_000_000_000
        assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<2_000_000;return r
    before=guard();out=HERE/'public_index_attempt01';out.mkdir(exist_ok=False)
    dump(out/'frozen_queries.json',dict(queries=QUERIES,pageSize=8,per_response_limit=400_000,source_bindings=[entry(Path(__file__)),entry(HERE/'PROTOCOL.md')]))
    context=ssl.create_default_context();assert context.check_hostname and context.verify_mode==ssl.CERT_REQUIRED
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=context));records=[]
    for i,q in enumerate(QUERIES):
        guard();url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode(dict(query=q,format='json',pageSize=8,resultType='core'))
        r=dict(query=q,complete=False,requested_url=url)
        try:
            with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRIResearchLiterature/1.0','Accept':'application/json'}),timeout=25) as response:
                data=response.read(400_001);assert len(data)<=400_000;r.update(http_status=response.status,effective_url=response.url)
            p=out/f'query{i}.json.gz';p.write_bytes(gzip.compress(data,mtime=0));v=json.loads(data)
            r.update(complete=True,hitCount=v['hitCount'],saved=entry(p),items=[{k:x.get(k) for k in ['id','pmcid','doi','title','authorString','firstPublicationDate','abstractText','isOpenAccess']} for x in v['resultList']['result']])
        except Exception as e:r['error']=dict(type=type(e).__name__,message=str(e))
        records.append(r);print(json.dumps(dict(query_index=i,complete=r['complete'],hitCount=r.get('hitCount'),items=[{k:x.get(k) for k in ['title','doi','pmcid']} for x in r.get('items',[])])),flush=True)
    result=dict(complete=all(x['complete'] for x in records),queries=records,resources_before=before,resources_after=guard(),
        elapsed_seconds=time.perf_counter()-started,new_maintexts_actually_read=0,patient_information_uploaded=False,patient_arrays_loaded=0,
        source_bindings=[entry(Path(__file__)),entry(HERE/'PROTOCOL.md')],publication_claim_confirmed=False,goal_status='active')
    dump(out/'receipt.json',result);return int(not result['complete'])
if __name__=='__main__':raise SystemExit(main())
