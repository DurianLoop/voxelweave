"""Three bounded primary queries, no fulltext/reading claim."""
import sys,json,time
from pathlib import Path
from urllib.parse import urlencode
from concurrent.futures import ThreadPoolExecutor
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
import retrieve_stronger_adaptation_primary as client
QUERIES=[('synthsr','TITLE:SynthSR'),('psacnn','TITLE:PSACNN'),
 ('vs_sr','TITLE_ABS:"vestibular schwannoma" AND TITLE_ABS:"super-resolution"')]
def main():
    sys.stdout.reconfigure(encoding='utf-8');r=client.resource_guard()
    assert r['workspace_free_bytes']>=8_009_000_000
    out=HERE/'index_attempt01';out.mkdir(exist_ok=False);client.OUT=out
    jobs=[(key,'https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urlencode(dict(query=query,format='json',pageSize=4,resultType='core')),'.json') for key,query in QUERIES]
    with ThreadPoolExecutor(max_workers=3) as pool:records=list(pool.map(lambda a:client.fetch(*a),jobs))
    for rec in records:
        if rec['complete']:
            q=json.loads((ROOT/rec['file']).read_text(encoding='utf-8'));rec['hit_count']=q['hitCount']
            rec['entries']=[{k:v.get(k) for k in ['id','source','doi','pmcid','title','authorString','firstPublicationDate','isOpenAccess','abstractText']} for v in q.get('resultList',{}).get('result',[])]
    result=dict(complete=all(v['complete'] for v in records),errors=[e for v in records for e in v['errors']],queries=QUERIES,records=records,
        maintexts_read=0,medical_arrays_loaded=0,GT_arrays_loaded=0,neural_forwards=0,confirmation_patients_opened=False,
        systematic_review_claimed=False,publication_claim_confirmed=False,goal_status='active',
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=client.sha(p)) for p in [Path(__file__),HERE/'PROTOCOL.md',Path(client.__file__)]])
    client.dump(out/'receipt.json',result)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<4_000_000
    print(json.dumps([dict(key=v['key'],complete=v['complete'],errors=v['errors'],hits=v.get('hit_count'),entries=[{k:e[k] for k in ['doi','pmcid','title','firstPublicationDate','isOpenAccess']} for e in v.get('entries',[])]) for v in records],ensure_ascii=False),flush=True)
    return int(not result['complete'])
if __name__=='__main__':raise SystemExit(main())
