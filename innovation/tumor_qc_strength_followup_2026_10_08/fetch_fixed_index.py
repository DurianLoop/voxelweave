"""Two bounded public primary-index queries to identify lesion QC and refinement prior art."""
import json,sys
from pathlib import Path
from urllib.parse import urlencode
from concurrent.futures import ThreadPoolExecutor
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
import retrieve_stronger_adaptation_primary as client

def main():
    sys.stdout.reconfigure(encoding='utf-8');client.resource_guard();out=HERE/'index_attempt01';out.mkdir(exist_ok=False);client.OUT=out
    queries=[('lesion_qc','(TITLE_ABS:"quality control" OR TITLE_ABS:"quality assessment") AND TITLE_ABS:segmentation AND (TITLE_ABS:glioma OR TITLE_ABS:lesion OR TITLE_ABS:tumor OR TITLE_ABS:tumour) AND FIRST_PDATE:[2000-01-01 TO 2026-10-08]'),
        ('MRI_quality_refinement','(TITLE_ABS:"segmentation quality" OR TITLE_ABS:"segmentation performance") AND (TITLE_ABS:MRI OR TITLE_ABS:"magnetic resonance") AND (TITLE_ABS:predict OR TITLE_ABS:prediction OR TITLE_ABS:refinement) AND FIRST_PDATE:[2000-01-01 TO 2026-10-08]')]
    jobs=[(key,'https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urlencode({'query':query,'format':'json','pageSize':8,'resultType':'core'}),'.json') for key,query in queries]
    with ThreadPoolExecutor(max_workers=2) as pool:records=list(pool.map(lambda x:client.fetch(*x),jobs))
    for r in records:
        if not r['complete']:continue
        q=json.loads((ROOT/r['file']).read_text(encoding='utf-8'));r['hit_count']=q.get('hitCount')
        r['entries']=[{k:x.get(k) for k in ['id','source','title','authorString','doi','pmcid','isOpenAccess','pubYear','firstPublicationDate','abstractText']} for x in q.get('resultList',{}).get('result',[])]
    size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file());assert size<5_000_000
    r=dict(complete=all(r['complete'] for r in records),errors=[e for r in records for e in r['errors']],records=records,
        new_primary_maintexts_read=0,abstracts_not_counted_as_maintexts=True,automatic_retries=False,
        MR_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,CUDA_initialized=False,
        previous_goal_turn_classification='progress',current_training_session=29823,training_observed_live_this_turn=True,
        publication_claim_confirmed=False,goal_status='active',resources=client.resource_guard(),
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=client.sha(p)) for p in [Path(__file__),HERE/'PROTOCOL.md',Path(client.__file__)]])
    client.dump(out/'receipt.json',r);print(json.dumps(r,ensure_ascii=False),flush=True);return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
