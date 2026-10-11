"""Two exact-title repo searches plus an actually indexed anonymous publisher endpoint."""
import sys,json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlencode
import query_author_sources as client
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'index_attempt03'

def main():
    sys.stdout.reconfigure(encoding='utf-8');client.base.own_priority();client.previous.resource_guard()
    index=ROOT/'seranet_identity_prior_art_2026_10_08/index_attempt03/receipt.json'
    q=json.loads(index.read_text(encoding='utf-8'))
    e=next(e for r in q['records'] for e in r.get('entries',[]) if e.get('DOI')=='10.1016/j.imavis.2024.105200')
    url=next(e['URL'] for e in e['link'] if e['content-type']=='text/plain')
    assert url.startswith('https://api.elsevier.com/content/article/PII:S0262885624003056')
    OUT.mkdir(exist_ok=False);client.OUT=OUT
    jobs=[('acar_exact_readme','https://api.github.com/search/repositories?'+urlencode({'q':'"Segmentation-Aware MRI Reconstruction" in:readme','per_page':5}),'repo'),
          ('xu_exact_readme','https://api.github.com/search/repositories?'+urlencode({'q':'"Segmentation-aware MRI subsampling" in:readme','per_page':5}),'repo'),
          ('xu_publisher_text',url,'landing')]
    with ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(client.fetch,jobs))
    result=dict(complete=all(r['complete'] for r in rows),errors=[e for r in rows for e in r['errors']],records=rows,
        source_bindings=[client.base.entry(p) for p in (Path(__file__),HERE/'AUTHOR_SEARCH_SELECTION.md',index)],
        resource_snapshot=client.previous.resource_guard(),public_GET_only=True,authentication_used=False,
        new_primary_papers_read=0,medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0)
    client.base.new(OUT/'receipt.json',result)
    for r in rows:
        display={k:r[k] for k in ('key','complete','HTTP_status','effective_url','total_count','page_title','errors') if k in r}
        if 'entries' in r:display['entries']=[{k:e[k] for k in ('full_name','html_url','description')} for e in r['entries']]
        print(json.dumps(display,ensure_ascii=False),flush=True)
    return int(not result['complete'])
if __name__=='__main__':raise SystemExit(main())
