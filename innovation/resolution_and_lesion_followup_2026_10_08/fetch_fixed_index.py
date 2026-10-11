"""Bounded primary screening, not fulltext reading."""
import sys,json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlencode
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
import retrieve_stronger_adaptation_primary as client
QUERIES=[('resolution','TITLE_ABS:segmentation AND TITLE_ABS:MRI AND (TITLE_ABS:"resolution-agnostic" OR TITLE_ABS:"resolution robust" OR TITLE_ABS:"resolution robustness" OR TITLE_ABS:"resolution-independent") AND FIRST_PDATE:[2022-01-01 TO 2026-10-08]'),
 ('small_lesion','TITLE_ABS:segmentation AND (TITLE_ABS:MRI OR TITLE_ABS:"magnetic resonance") AND (TITLE_ABS:"small lesions" OR TITLE_ABS:"lesion-wise loss" OR TITLE_ABS:"lesion-wise") AND FIRST_PDATE:[2024-01-01 TO 2026-10-08]'),
 ('sampling','TITLE_ABS:segmentation AND (TITLE_ABS:"anti-aliasing" OR TITLE_ABS:"label-preserving" OR TITLE_ABS:"interpolation artifacts") AND FIRST_PDATE:[2022-01-01 TO 2026-10-08]')]
def main():
    sys.stdout.reconfigure(encoding='utf-8');client.resource_guard()
    out=HERE/'index_attempt01';out.mkdir(exist_ok=False);client.OUT=out
    jobs=[(k,'https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urlencode(dict(query=q,format='json',pageSize=6,resultType='core')),'.json') for k,q in QUERIES]
    with ThreadPoolExecutor(max_workers=3) as pool:records=list(pool.map(lambda a:client.fetch(*a),jobs))
    for r in records:
        if r['complete']:
            q=json.loads((ROOT/r['file']).read_text(encoding='utf-8'));r['hit_count']=q.get('hitCount')
            r['entries']=[{k:x.get(k) for k in ['id','source','title','authorString','doi','pmcid','firstPublicationDate','isOpenAccess','abstractText']} for x in q.get('resultList',{}).get('result',[])]
    receipt=dict(complete=all(r['complete'] for r in records),errors=[e for r in records for e in r['errors']],queries=QUERIES,records=records,
        fulltexts_read=0,systematic_review_claimed=False,medical_arrays_loaded=0,neural_forwards=0,CUDA_initialized=False,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=client.sha(p)) for p in [Path(__file__),HERE/'PROTOCOL.md',Path(client.__file__)]])
    client.dump(out/'receipt.json',receipt)
    print(json.dumps([dict(key=r['key'],complete=r['complete'],errors=r['errors'],hits=r.get('hit_count'),entries=[{k:x.get(k) for k in ['title','doi','pmcid','firstPublicationDate']} for x in r.get('entries',[])]) for r in records],ensure_ascii=False),flush=True)
    return int(not receipt['complete'])
if __name__=='__main__':raise SystemExit(main())
