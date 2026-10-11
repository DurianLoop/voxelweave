"""Three adaptive followup requests, based on the preceding actual index results."""
import sys,json
from pathlib import Path
from urllib.parse import urlencode
from concurrent.futures import ThreadPoolExecutor
import query_author_sources as client
HERE=Path(__file__).resolve().parent;OUT=HERE/'index_attempt02'

def main():
    sys.stdout.reconfigure(encoding='utf-8');client.base.own_priority();client.previous.resource_guard()
    index=HERE/'index_attempt01/receipt.json';q=json.loads(index.read_text(encoding='utf-8'))
    row=next(r for r in q['records'] if r['key']=='xu_openalex')
    url=next(e['landing_page_url'] for e in row['metadata']['locations'] if e['id'].endswith('11527/43339'))
    assert url=='https://hdl.handle.net/11527/43339'
    OUT.mkdir(exist_ok=False);client.OUT=OUT
    jobs=[('xu_itu',url,'landing'),
        ('seranet_readme_repos','https://api.github.com/search/repositories?'+urlencode({'q':'1812.02068 in:readme','per_page':5}),'repo'),
        ('teacher_readme_repos','https://api.github.com/search/repositories?'+urlencode({'q':'"Multi-task MR Imaging" in:readme','per_page':5}),'repo')]
    with ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(client.fetch,jobs))
    result=dict(complete=all(r['complete'] for r in rows),errors=[e for r in rows for e in r['errors']],records=rows,
        source_bindings=[client.base.entry(p) for p in (Path(__file__),HERE/'PRIMARY_SELECTION.md',index)],
        resource_snapshot=client.previous.resource_guard(),medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0)
    client.base.new(OUT/'receipt.json',result)
    for r in rows:
        display={k:r[k] for k in ('key','complete','HTTP_status','effective_url','total_count','page_title','errors') if k in r}
        if 'entries' in r:display['entries']=[{k:e[k] for k in ('full_name','html_url','description')} for e in r['entries']]
        if r['key']=='xu_itu':display['public_links']=r.get('public_links');display['metadata']=r.get('metadata')
        print(json.dumps(display,ensure_ascii=False),flush=True)
    return int(not result['complete'])
if __name__=='__main__':raise SystemExit(main())
