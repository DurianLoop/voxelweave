"""Read three small files at the resolved fixed commit and verify Git blob bytes."""
import sys,json,time,ssl,urllib.request,hashlib
from pathlib import Path
import search_primary_candidates as h
HERE=Path(__file__).resolve().parent
SELECTION=['README.md','compute_maps/compute_raw_maps.py','compute_maps/compute_specific_maps.py']
def main():
 sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();h.guard();tree=json.loads((HERE/'hallucination_author_tree_attempt02/receipt.json').read_text(encoding='utf-8'));assert tree['complete'];out=HERE/'hallucination_author_files_attempt01';out.mkdir(exist_ok=False);records=[]
 for i,name in enumerate(SELECTION):
  expected=next(v for v in tree['files'] if v['path']==name);assert expected['bytes']<100000
  url='https://raw.githubusercontent.com/'+tree['canonical_repo']+'/'+tree['commit']+'/'+name;row=dict(author_path=name,requested_url=url,complete=False)
  try:
   h.guard();ctx=ssl.create_default_context();op=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ctx),h.Redirect());req=urllib.request.Request(url,headers={'User-Agent':'MRI-literature-review/1.0','Accept':'text/plain'})
   with op.open(req,timeout=30) as response:
    data=response.read(100001);assert len(data)<=100000 and response.status==200;row.update(status=response.status,effective_url=response.geturl())
   blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();assert len(data)==expected['bytes'] and blob==expected['blob_sha1']
   p=out/(str(i).zfill(2)+'_'+Path(name).name)
   with p.open('xb') as f:f.write(data)
   row.update(complete=True,git_blob_sha1=blob,git_blob_exactly_verified=True,lines=len(data.decode('utf-8').splitlines()),source=dict(path=p.relative_to(h.ROOT).as_posix(),bytes=len(data),sha256=h.sha(p)))
  except Exception as e:row['error']=repr(e)
  records.append(row);h.dump(out/(str(i).zfill(2)+'_receipt.json'),row);print(json.dumps(row,ensure_ascii=False),flush=True)
 r=dict(complete=all(v['complete'] for v in records),errors=[v['error'] for v in records if not v['complete']],commit=tree['commit'],repository=tree['canonical_repo'],records=records,
  author_files_actually_read=0,author_implementation_executed=False,elapsed_seconds=time.perf_counter()-started,resources=h.guard());h.dump(out/'receipt.json',r);return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
