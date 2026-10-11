"""Four bounded public repository searches; no source execution or installation."""
import sys,json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlencode
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'author_index_attempt01'
sys.path.insert(0,str(ROOT/'author_implementation_and_sampling_prior_art_2026_10_08'))
import query_author_sources as client

def main():
    sys.stdout.reconfigure(encoding='utf-8');client.previous.resource_guard();OUT.mkdir(exist_ok=False);client.OUT=OUT
    queries=[('rd_name','RD-ViT'),('rd_id','"2605.03999" in:readme'),('hifi_name','HiFi-MambaV2'),('hifi_id','"2511.18534" in:readme')]
    jobs=[(key,'https://api.github.com/search/repositories?'+urlencode({'q':q,'per_page':5}),'repo') for key,q in queries]
    with ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(client.fetch,jobs))
    result=dict(complete=all(r['complete'] for r in rows),errors=[e for r in rows for e in r['errors']],records=rows,
        source_bindings=[client.base.entry(p) for p in (Path(__file__),HERE/'AUTHOR_LOOKUP_PLAN.md',HERE/'visual_attempt01/receipt.json')],
        resource_snapshot=client.previous.resource_guard(),public_GET_only=True,authentication_used=False,
        source_code_executed=False,medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0)
    client.base.new(OUT/'receipt.json',result)
    for r in rows:print(json.dumps({k:r.get(k) for k in ('key','complete','HTTP_status','total_count','entries','errors')},ensure_ascii=False),flush=True)
    return int(not result['complete'])
if __name__=='__main__':raise SystemExit(main())
