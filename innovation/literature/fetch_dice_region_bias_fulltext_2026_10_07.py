"""Obtain the exact public v4 author manuscript; never count acquisition as reading."""
import hashlib,json,sys,urllib.request
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/dice_region_bias_fulltext_2026-10-07'
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    row=dict(created_utc=datetime.now(timezone.utc).isoformat(),arxiv='2104.08717v4',
             doi='10.1016/j.media.2023.103015',actual_reading_completed=False,
             url='https://arxiv.org/html/2104.08717v4',complete=False,
             script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    try:
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(row['url'],timeout=20) as response:
            raw=response.read(8_000_001);row.update(http_status=response.status,content_type=response.headers.get('Content-Type'))
        path=OUT/'html_v4_attempt01.response';path.write_bytes(raw);assert len(raw)<=8_000_000
        assert b'<article' in raw and b'Hidden Region' in raw
        row.update(complete=True,file=path.name,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
    except Exception as e:row['error']=type(e).__name__+': '+str(e)
    (OUT/'retrieval_attempt01.json').write_text(json.dumps(row,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(row),flush=True);return int(not row['complete'])
if __name__=='__main__':raise SystemExit(main())
