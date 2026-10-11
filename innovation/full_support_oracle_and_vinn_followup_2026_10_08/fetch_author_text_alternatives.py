"""Three bounded, public, alternative GETs; acquisition is not reading."""
import sys,time,json,ssl
from pathlib import Path
from urllib.request import Request,build_opener,ProxyHandler,HTTPSHandler,HTTPRedirectHandler
from urllib.parse import urlsplit
from concurrent.futures import ThreadPoolExecutor
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import entry,dump,resource_guard
class Redirect(HTTPRedirectHandler):
    max_redirections=3
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        assert urlsplit(newurl).scheme=='https';return super().redirect_request(req,fp,code,msg,headers,newurl)
def fetch(job):
    key,url,suffix=job;tick=time.perf_counter();r=dict(key=key,requested_url=url,complete=False,errors=[],actual_reading_completed=False)
    try:
        resource_guard();ctx=ssl.create_default_context();assert ctx.check_hostname and ctx.verify_mode==ssl.CERT_REQUIRED
        op=build_opener(ProxyHandler({}),HTTPSHandler(context=ctx),Redirect())
        with op.open(Request(url,headers={'User-Agent':'MRI-primary-research/1.0'}),timeout=30) as h:
            r.update(HTTP_status=h.status,effective_url=h.geturl());assert urlsplit(h.geturl()).scheme=='https'
            content=h.read(500001);assert len(content)<=500000 and time.perf_counter()-tick<35
            dump(HERE/'author_sources_attempt01'/(key+'_headers.json'),dict(status=h.status,headers=dict(h.headers)))
        path=HERE/'author_sources_attempt01'/(key+suffix)
        with path.open('xb') as f:f.write(content)
        r.update(complete=True,source_binding=entry(path),preview=content[:200].decode('utf-8',errors='replace'))
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e))
    r['elapsed_seconds']=time.perf_counter()-tick;return r
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard();out=HERE/'author_sources_attempt01';out.mkdir(exist_ok=False)
    jobs=[('vinn_bioc','https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/PMC9801435/unicode','.json'),
        ('lesion_ensemble_bioc','https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/PMC13148016/unicode','.json'),
        ('vinn_pmc_html','https://pmc.ncbi.nlm.nih.gov/articles/PMC9801435/','.html')]
    with ThreadPoolExecutor(max_workers=3) as pool:records=list(pool.map(fetch,jobs))
    receipt=dict(complete=all(r['complete'] for r in records),errors=[e for r in records for e in r['errors']],records=records,
        actual_primary_maintexts_completed=0,medical_arrays_loaded=0,GT_arrays_loaded=0,neural_forwards=0,CUDA_initialized=False,
        source_bindings=[entry(p) for p in [Path(__file__),HERE/'AUTHOR_TEXT_SOURCE_PROTOCOL.md']])
    dump(out/'receipt.json',receipt);assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    print(json.dumps(records,ensure_ascii=False),flush=True);return int(not receipt['complete'])
if __name__=='__main__':raise SystemExit(main())
