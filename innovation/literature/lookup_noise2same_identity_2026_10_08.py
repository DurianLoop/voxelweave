"""Public metadata lookup after a retained wrong arXiv-ID acquisition. No paper-read claim."""
import hashlib
import json
import sys
import urllib.request
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/blindspot_dependence_primary_2026-10-08'


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    url='https://api.openalex.org/works?search=Noise2Same&per-page=3'
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRI-public-literature/1.0'}),timeout=30) as response:
        data=response.read(2_000_001)
        assert len(data)<=2_000_000
        status=response.status
        final_url=response.geturl()
    raw=OUT/'noise2same_openalex_identity_attempt01.response'
    with raw.open('xb') as f:
        f.write(data)
    result=json.loads(data)
    rows=[dict(id=r['id'],title=r['title'],doi=r.get('doi'),publication_year=r['publication_year'],
               authors=[a['author']['display_name'] for a in r['authorships']],
               primary_location=r['primary_location'],locations=r.get('locations',[])) for r in result['results']]
    receipt=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],requested_url=url,
        final_url=final_url,http_status=status,response_path=raw.relative_to(ROOT).as_posix(),
        response_sha256=hashlib.sha256(data).hexdigest(),records=rows,new_primary_papers_read=0,
        wrong_2010_12062_source_retained_and_excluded=True)
    with (OUT/'noise2same_identity_lookup_attempt01.json').open('x',encoding='utf-8') as f:
        json.dump(receipt,f,ensure_ascii=False,indent=2)
        f.write('\n')
    print(json.dumps(rows,ensure_ascii=False),flush=True)
    return 0


if __name__=='__main__':
    raise SystemExit(main())
