"""Exact-DOI public indexing only; bounded, provenance saved, never counted as fulltext reading."""
import json,sys,time
from pathlib import Path
from urllib.parse import urlencode
from concurrent.futures import ThreadPoolExecutor
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
import retrieve_stronger_adaptation_primary as client

def main():
    sys.stdout.reconfigure(encoding='utf-8');client.resource_guard();out=HERE/'robust_qc_index_attempt01';out.mkdir(exist_ok=False);client.OUT=out
    jobs=[('robust_qc_exact_doi','https://api.crossref.org/works/10.1073%2Fpnas.2216399120','.json'),
          ('robust_qc_epmc','https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urlencode({'query':'DOI:10.1073/pnas.2216399120','format':'json','pageSize':3,'resultType':'core'}),'.json')]
    with ThreadPoolExecutor(max_workers=2) as pool:records=list(pool.map(lambda x:client.fetch(*x),jobs))
    for r in records:
        if not r['complete']:continue
        q=json.loads((ROOT/r['file']).read_text(encoding='utf-8'))
        if r['key']=='robust_qc_exact_doi':
            q=q['message'];r['identity']={k:q.get(k) for k in ['title','DOI','author','published','URL']}
            assert q['DOI'].lower()=='10.1073/pnas.2216399120'
        else:
            r['hit_count']=q.get('hitCount');r['entries']=[{k:x.get(k) for k in ['title','doi','pmcid','id','source','authorString','pubYear','isOpenAccess','abstractText']} for x in q.get('resultList',{}).get('result',[])]
    receipt=dict(complete=all(r['complete'] for r in records),errors=[e for r in records for e in r['errors']],records=records,
        primary_text_papers_read=0,automatic_retries=False,medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,
        neural_forwards=0,CUDA_initialized=False,resources=client.resource_guard(),
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=client.sha(p)) for p in [Path(__file__),HERE/'ROBUST_QC_FOLLOWUP_PROTOCOL.md',Path(client.__file__)]])
    client.dump(out/'receipt.json',receipt);print(json.dumps(receipt,ensure_ascii=False),flush=True)
    return int(not receipt['complete'])
if __name__=='__main__':raise SystemExit(main())
