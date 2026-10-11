"""Verify the counterpoint cited by Eldesokey before acquiring its original."""
import hashlib,json,urllib.parse,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/sparse_dense_counterpoint_2026-10-07'
TITLE='Sparse and Dense Data with CNNs: Depth Completion and Semantic Segmentation'
def main():
    OUT.mkdir(exist_ok=False);url='https://api.openalex.org/works?'+urllib.parse.urlencode({'search':TITLE,'per-page':3})
    r=dict(query_title=TITLE,url=url,reading_performed=False,verified_candidates=[])
    try:
        with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(urllib.request.Request(url,headers={'User-Agent':'MRI-local-research/1.0'}),timeout=30) as response:
            b=response.read(2_000_001);r['status']=response.status
        assert len(b)<=2_000_000;(OUT/'openalex_response.json').write_bytes(b)
        r['response_sha256']=hashlib.sha256(b).hexdigest()
        for v in json.loads(b)['results']:
            if v['title'].casefold()==TITLE.casefold():
                r['verified_candidates'].append(dict(title=v['title'],doi=v.get('doi'),id=v['id'],
                    authors=[a['author']['display_name'] for a in v['authorships']],
                    locations=[{k:x.get(k) for k in ('pdf_url','landing_page_url','version')} for x in v['locations']]))
        r['success']=bool(r['verified_candidates'])
    except Exception as e:r.update(success=False,error=f'{type(e).__name__}: {e}')
    with (OUT/'identity_attempt01.json').open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2)
    print(json.dumps(r,ensure_ascii=False));return int(not r['success'])
if __name__=='__main__':raise SystemExit(main())
