"""Bounded larger original PDF route; old truncated-size failure is preserved."""
import hashlib,json,shutil,subprocess,sys,urllib.request
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'source_cache/thumbnail_instance_normalization_v2_2026-10-07'
URL='https://arxiv.org/pdf/2103.11784v3'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),url=URL,
        previous_attempt='source_cache/thumbnail_instance_normalization_2026-10-07/acquisition_attempt01.json',
        response_limit_bytes=60_000_000,actual_reading_completed=False,fulltext_acquired=False)
    try:
        assert shutil.disk_usage(OUT).free>=8_100_000_000
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(URL,timeout=25) as resp:
            r.update(http_status=resp.status,final_url=resp.url,response_headers=dict(resp.headers.items()))
            raw=resp.read(60_000_001)
        response=OUT/'primary_pdf.response';response.write_bytes(raw)
        r.update(raw_file=response.name,raw_sha256=sha(response),raw_bytes=len(raw),raw_prefix=raw[:20].decode('ascii',errors='replace'))
        assert len(raw)<=60_000_000,'Response exceeds new bounded paper budget'
        assert raw.startswith(b'%PDF'),'Primary PDF route returned non-PDF content'
        # Keep one physical copy with .pdf suffix; response identity persists in the record.
        pdf=OUT/'thumbnail_instance_norm.pdf';response.rename(pdf);r['raw_file']=pdf.name
        txt=OUT/'thumbnail_instance_norm_layout.txt';command=[shutil.which('pdftotext'),'-layout','-enc','UTF-8',str(pdf),str(txt)]
        run=subprocess.run(command,capture_output=True,timeout=40);assert run.returncode==0,run.stderr
        pages=txt.read_text(encoding='utf-8').split('\f')
        if not pages[-1].strip():pages.pop()
        pagefile=OUT/'thumbnail_instance_norm_pages.json';pagefile.write_text(json.dumps([dict(page=i+1,text=t) for i,t in enumerate(pages)],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        r.update(fulltext_acquired=True,pdf_file=pdf.name,pdf_sha256=sha(pdf),pages=len(pages),
            text_file=txt.name,text_sha256=sha(txt),pages_file=pagefile.name,pages_sha256=sha(pagefile),extraction_command=command)
    except Exception as e:r['error']=type(e).__name__+': '+str(e)
    (OUT/'acquisition_attempt01.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:r.get(k) for k in ('fulltext_acquired','raw_bytes','raw_prefix','response_headers','pages','error')},ensure_ascii=False),flush=True)
    return int(not r['fulltext_acquired'])
if __name__=='__main__':raise SystemExit(main())
