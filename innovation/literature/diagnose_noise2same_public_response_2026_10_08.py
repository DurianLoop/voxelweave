"""Inspect only public response metadata and first 64 bytes after a retained acquisition assertion."""
import json
import sys
import urllib.request
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/blindspot_dependence_primary_2026-10-08'


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    source=json.loads((OUT/'noise2same_official_identity_attempt01.json').read_text(encoding='utf-8'))
    urls=[u for u in source['actual_public_PDF_links'] if u.endswith('-Paper.pdf')]
    assert len(urls)==1
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(urllib.request.Request(urls[0],headers={'User-Agent':'MRI-public-literature/1.0'}),timeout=30) as response:
        prefix=response.read(64)
        record=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
            requested_url=urls[0],final_url=response.geturl(),http_status=response.status,
            content_type=response.headers.get('Content-Type'),content_length=response.headers.get('Content-Length'),
            first_64_bytes_ascii=prefix.decode('ascii',errors='replace'),bytes_actually_read=len(prefix),
            PDF_magic_matched=prefix.startswith(b'%PDF'),new_primary_papers_read=0,
            prior_acquisition_tool_chunk='a02665',prior_acquisition_tool_exit=1)
    with (OUT/'noise2same_public_response_diagnostic_attempt01.json').open('x',encoding='utf-8') as f:
        json.dump(record,f,ensure_ascii=False,indent=2)
        f.write('\n')
    print(json.dumps(record,ensure_ascii=False),flush=True)
    return 0


if __name__=='__main__':
    raise SystemExit(main())
