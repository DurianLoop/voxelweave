"""Three bounded anonymous metadata requests; preserve errors and raw responses."""
import json, sys, time, ssl, traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlencode
from urllib.request import build_opener, ProxyHandler, HTTPSHandler, Request
from urllib.error import HTTPError
import query_seranet_stdlib_v3 as prior

HERE = Path(__file__).resolve().parent
OUT = HERE / 'location_attempt01'
base = prior.base

def fetch(job):
    key, url = job
    start = time.perf_counter()
    row = dict(key=key, requested_url=url, complete=False, errors=[])
    try:
        ctx = ssl.create_default_context()
        opener = build_opener(ProxyHandler({}), HTTPSHandler(context=ctx), prior.LimitedRedirect())
        req = Request(url, headers={'User-Agent':'MRI-innovation-literature-audit/1.0'})
        with opener.open(req, timeout=30) as response:
            row.update(HTTP_status=response.status, effective_url=response.geturl())
            base.new(OUT / (key + '_headers.json'), dict(status=response.status, headers=dict(response.headers)))
            blocks, total = [], 0
            while True:
                b = response.read(65536)
                if not b:
                    break
                total += len(b)
                assert total <= 3_000_000 and time.perf_counter() - start <= 35
                blocks.append(b)
            body = b''.join(blocks)
        dest = OUT / (key + '.json')
        with dest.open('xb') as f:
            f.write(body)
        data = json.loads(body)
        row['response_binding'] = base.entry(dest)
        if key == 'acar_openalex':
            row['metadata'] = {k:data.get(k) for k in ('id','doi','title','authorships','open_access','best_oa_location','locations')}
        elif key == 'acar_semantic_scholar':
            row['metadata'] = data
        else:
            row['count'] = data.get('meta',{}).get('count')
            row['entries'] = [{k:e.get(k) for k in ('id','doi','title','authorships','open_access','best_oa_location')} for e in data.get('results',[])]
        row['complete'] = True
    except HTTPError as e:
        row.update(HTTP_status=e.code, effective_url=e.geturl())
        body = e.read(3_000_001)
        assert len(body) <= 3_000_000
        p = OUT / (key + '_error.bin')
        with p.open('xb') as f:
            f.write(body)
        row['error_response'] = base.entry(p)
        row['errors'].append(type(e).__name__ + ': ' + str(e))
    except Exception as e:
        row['errors'].append(type(e).__name__ + ': ' + str(e))
        row['traceback'] = traceback.format_exc()
    row['elapsed_seconds'] = time.perf_counter() - start
    return row

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    base.own_priority()
    resources = prior.resource_guard()
    OUT.mkdir(exist_ok=False)
    doi = '10.1007/978-3-031-17247-2_6'
    jobs = [
        ('acar_openalex','https://api.openalex.org/works/https://doi.org/' + quote(doi,safe='/')),
        ('acar_semantic_scholar','https://api.semanticscholar.org/graph/v1/paper/DOI:' + quote(doi,safe='/') + '?' + urlencode({'fields':'title,authors,year,externalIds,openAccessPdf,url'})),
        ('seranet_openalex','https://api.openalex.org/works?' + urlencode({'search':'SERANet','per-page':8})),
    ]
    with ThreadPoolExecutor(max_workers=3) as pool:
        rows = list(pool.map(fetch,jobs))
    q = dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=all(r['complete'] for r in rows),
             errors=[e for r in rows for e in r['errors']],records=rows,resource_snapshot=resources,
             source_bindings=[base.entry(p) for p in (Path(__file__),HERE/'METADATA_FOLLOWUP_PLAN.md',HERE/'index_attempt03/receipt.json')],
             public_GET_only=True,TLS_verification_disabled=False,automatic_retries=False,authentication_used=False,
             medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0)
    base.new(OUT/'receipt.json',q)
    for r in rows:
        text = {k:r[k] for k in ('key','complete','HTTP_status','count','metadata','entries','errors') if k in r}
        print(json.dumps(text,ensure_ascii=False),flush=True)
    return int(not q['complete'])

if __name__ == '__main__':
    raise SystemExit(main())
