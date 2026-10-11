import hashlib,json,sys,urllib.request,urllib.parse
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/dice_followup_metadata_2026-10-07'
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}));rows=[]
    queries=[('generalised_dice','id_list=1707.03237'),('dice_semimetric',urllib.parse.urlencode(dict(search_query='ti:"Dice Semimetric"',start=0,max_results=3)))]
    for name,query in queries:
        url='https://export.arxiv.org/api/query?'+query;row=dict(name=name,url=url,complete=False,actual_reading_completed=False)
        try:
            with opener.open(url,timeout=18) as response:raw=response.read(2_000_001);row['http_status']=response.status
            assert len(raw)<=2_000_000;path=OUT/(name+'_attempt01.response');path.write_bytes(raw)
            row.update(complete=True,file=path.name,sha256=hashlib.sha256(raw).hexdigest())
        except Exception as e:row['error']=type(e).__name__+': '+str(e)
        rows.append(row);(OUT/'attempt01.json').write_text(json.dumps(dict(created_utc=datetime.now(timezone.utc).isoformat(),
            script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),routes=rows),indent=2)+'\n',encoding='utf-8')
        print(json.dumps(row),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
