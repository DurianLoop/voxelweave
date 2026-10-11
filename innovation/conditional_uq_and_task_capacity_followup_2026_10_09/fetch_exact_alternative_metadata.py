"""Read two exact DOI metadata from a different public provider, no retry."""
import sys,json,time,urllib.request,urllib.parse,ssl
from pathlib import Path
import search_primary_candidates as h
HERE=Path(__file__).resolve().parent
DOIS=['10.1016/j.neuroimage.2020.117366','10.1109/TMI.2021.3077857']
def main():
 sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();h.guard();out=HERE/'crossref_attempt01';out.mkdir(exist_ok=False);rows=[]
 for i,doi in enumerate(DOIS):
  h.guard();url='https://api.crossref.org/works/'+urllib.parse.quote(doi,safe='');row=dict(doi=doi,requested_url=url,complete=False)
  try:
   ctx=ssl.create_default_context();op=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ctx),h.Redirect())
   req=urllib.request.Request(url,headers={'User-Agent':'MRI-literature-review/1.0','Accept':'application/json'})
   with op.open(req,timeout=30) as response:
    data=response.read(500001);assert len(data)<=500000 and response.status==200
    row.update(status=response.status,effective_url=response.geturl(),headers=dict(response.headers.items()))
   v=json.loads(data);m=v['message'];assert m['DOI'].casefold()==doi.casefold();p=out/(str(i).zfill(2)+'.json')
   with p.open('xb') as f:f.write(data)
   row.update(complete=True,source=dict(path=p.relative_to(h.ROOT).as_posix(),bytes=len(data),sha256=h.sha(p)),title=m['title'],links=m.get('link'),resource=m.get('resource'),authors=m.get('author'),published=m.get('published'))
  except Exception as e:row['error']=repr(e)
  rows.append(row);h.dump(out/(str(i).zfill(2)+'_receipt.json'),row);print(json.dumps(row,ensure_ascii=False),flush=True)
 h.dump(out/'receipt.json',dict(complete=all(v['complete'] for v in rows),errors=[v['error'] for v in rows if not v['complete']],records=rows,elapsed_seconds=time.perf_counter()-started,fulltexts_actually_read=0,resources=h.guard()))
 return int(not all(v['complete'] for v in rows))
if __name__=='__main__':raise SystemExit(main())
