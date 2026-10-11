"""Public author and arXiv metadata discovery; does not assert full-text reading."""
import hashlib,json,sys,urllib.request,urllib.parse
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/small_target_loss_routes_2026-10-07'
ROUTES=[('author_readme','https://raw.githubusercontent.com/by-liu/SegLossBias/main/README.md'),
        ('arxiv_title','https://export.arxiv.org/api/query?'+urllib.parse.urlencode(dict(
            search_query='ti:"Do we really need Dice"',start=0,max_results=3)))]

def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}));rows=[]
    for name,url in ROUTES:
        row=dict(name=name,url=url,complete=False,actual_reading_completed=False)
        try:
            with opener.open(url,timeout=18) as response:
                raw=response.read(2_000_001);row.update(http_status=response.status,content_type=response.headers.get('Content-Type'))
            path=OUT/(name+'_attempt01.response');path.write_bytes(raw);assert len(raw)<=2_000_000
            row.update(complete=True,bytes=len(raw),file=path.name,sha256=hashlib.sha256(raw).hexdigest())
        except Exception as e:row['error']=type(e).__name__+': '+str(e)
        rows.append(row);print(json.dumps(row),flush=True)
        (OUT/'attempt01.json').write_text(json.dumps(dict(created_utc=datetime.now(timezone.utc).isoformat(),
            script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),routes=rows),indent=2)+'\n',encoding='utf-8')
    return 0

if __name__=='__main__':raise SystemExit(main())
