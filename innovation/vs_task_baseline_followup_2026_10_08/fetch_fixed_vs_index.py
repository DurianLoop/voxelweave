"""Bounded two-query source screening; downloads are not fulltext reading."""
import json,sys
from pathlib import Path
from urllib.parse import urlencode
from concurrent.futures import ThreadPoolExecutor
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
import retrieve_stronger_adaptation_primary as client
QUERIES=[('recent_vs_segmentation','TITLE_ABS:"vestibular schwannoma" AND TITLE_ABS:segmentation AND FIRST_PDATE:[2023-01-01 TO 2026-10-08]'),
    ('t2_vs_models','TITLE_ABS:"vestibular schwannoma" AND (TITLE_ABS:"T2" OR TITLE_ABS:"non-contrast") AND (TITLE_ABS:"segmentation" OR TITLE_ABS:"deep learning") AND FIRST_PDATE:[2020-01-01 TO 2026-10-08]')]
def main():
    sys.stdout.reconfigure(encoding='utf-8');resources=client.resource_guard()
    out=HERE/'index_attempt01';out.mkdir(exist_ok=False);client.OUT=out
    jobs=[(k,'https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urlencode(dict(query=q,format='json',pageSize=8,resultType='core')),'.json') for k,q in QUERIES]
    with ThreadPoolExecutor(max_workers=2) as pool:records=list(pool.map(lambda x:client.fetch(*x),jobs))
    for r in records:
        if r['complete']:
            q=json.loads((ROOT/r['file']).read_text(encoding='utf-8'));r['hit_count']=q.get('hitCount')
            r['entries']=[{k:x.get(k) for k in ['id','source','title','authorString','doi','pmcid','firstPublicationDate','pubYear','abstractText','isOpenAccess','pubTypeList']} for x in q.get('resultList',{}).get('result',[])]
    receipt=dict(complete=all(r['complete'] for r in records),errors=[e for r in records for e in r['errors']],queries=QUERIES,records=records,
        fulltexts_read=0,systematic_review_claimed=False,medical_arrays_loaded=0,model_arrays_loaded=0,GT_arrays_loaded=0,neural_forwards=0,CUDA_initialized=False,
        publication_claim_confirmed=False,goal_status='active',resources=resources,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=client.sha(p)) for p in [Path(__file__),HERE/'PROTOCOL.md',Path(client.__file__)]])
    client.dump(out/'receipt.json',receipt)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    print(json.dumps([dict(key=r['key'],complete=r['complete'],errors=r['errors'],hits=r.get('hit_count'),entries=[{k:x.get(k) for k in ['title','doi','pmcid','firstPublicationDate']} for x in r.get('entries',[])]) for r in records],ensure_ascii=False),flush=True)
    return int(not receipt['complete'])
if __name__=='__main__':raise SystemExit(main())
