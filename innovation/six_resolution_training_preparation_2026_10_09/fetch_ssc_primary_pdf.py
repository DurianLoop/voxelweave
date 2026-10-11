"""One DOI-exact metadata-linked public PDF request; preserve a real denial without bypass."""
import sys,time,ssl,json,gzip,urllib.request,urllib.error
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,entry,dump,bind,resource_guard
started=time.perf_counter();out=HERE/'ssc_primary_pdf_attempt01';out.mkdir(exist_ok=False)
meta=HERE/'gin_ssc_identity_attempt01/ssc_metadata.json.gz';v=json.loads(gzip.decompress(meta.read_bytes()))['resultList']['result'][0]
assert v['doi']=='10.1007/978-3-642-40811-3_24'
url=next(q['url'] for q in v['fullTextUrlList']['fullTextUrl'] if q['availabilityCode']=='F' and q['documentStyle']=='pdf')
r=dict(complete=False,errors=[],requested_url=url,doi=v['doi'],title=v['title'],authorString=v['authorString'],
 maintext_actually_read=False,medical_data_uploaded=False,access_denial_not_bypassed=True,
 source_bindings=[entry(p) for p in [Path(__file__),HERE/'SSC_PRIMARY_PDF_PROTOCOL.md',meta]])
try:
 res=resource_guard();size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
 fov=ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09';fs=sum(p.stat().st_size for p in fov.rglob('*') if p.is_file())
 assert size+2_600_000<7_000_000 and fs<20_000_000
 assert res['workspace_free_bytes']-22_800_000-(7_000_000-size)-(20_000_000-fs)>=8_000_000_000
 opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ssl.create_default_context()))
 with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRIResearchLiterature/1.0'}),timeout=30) as response:
  data=response.read(2_500_001);r.update(effective_url=response.url,http_status=response.status,content_type=response.headers.get('Content-Type'))
  assert len(data)<=2_500_000 and data.startswith(b'%PDF-')
 target=out/'primary.pdf';target.write_bytes(data);r.update(complete=True,pdf=entry(target))
except urllib.error.HTTPError as e:
 body=e.read(3000);target=out/'http_error_excerpt.txt';target.write_bytes(body)
 r.update(http_status=e.code,effective_url=e.url,error_excerpt=entry(target));r['errors'].append(type(e).__name__+': '+str(e))
except Exception as e:r['errors'].append(type(e).__name__+': '+str(e))
r['elapsed_seconds']=time.perf_counter()-started;dump(out/'receipt.json',r);print(json.dumps(r,ensure_ascii=False),flush=True)
raise SystemExit(int(not r['complete']))
