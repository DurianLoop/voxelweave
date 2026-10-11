"""Acquire one fixed-v1 public preprint; no reading claim until actual review."""
import hashlib, json, shutil, subprocess, sys, urllib.request
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/agentic_restoration_primary_2026-10-07'
URL='https://www.preprints.org/manuscript/202609.1256/v1/download'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),
        doi='10.20944/preprints202609.1256.v1',url=URL,fulltext_acquired=False,actual_reading_completed=False,
        training_updates=0,gpu_updates=0)
    try:
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(URL,timeout=25) as response:
            raw=response.read(25_000_001);result.update(http_status=response.status,final_url=response.geturl(),content_type=response.headers.get('Content-Type'))
        rawfile=OUT/'download_attempt01.response';rawfile.write_bytes(raw);result.update(raw_file=rawfile.name,raw_sha256=sha(rawfile))
        assert len(raw)<=25_000_000 and raw.startswith(b'%PDF'), 'Public route did not return a within-budget PDF'
        pdf=OUT/'agentic_restoration_v1.pdf';pdf.write_bytes(raw)
        text=OUT/'agentic_restoration_v1_layout.txt'
        command=[shutil.which('pdftotext'),'-layout','-enc','UTF-8',str(pdf),str(text)]
        proc=subprocess.run(command,capture_output=True,timeout=30);assert proc.returncode==0,proc.stderr
        info=subprocess.run([shutil.which('pdfinfo'),str(pdf)],capture_output=True,timeout=20);assert info.returncode==0
        (OUT/'pdfinfo.txt').write_bytes(info.stdout)
        result.update(fulltext_acquired=True,pdf_file=pdf.name,pdf_sha256=sha(pdf),text_file=text.name,text_sha256=sha(text),extraction_command=command)
        print(text.read_text(encoding='utf-8')[:4500],flush=True)
    except Exception as e:result['error']=type(e).__name__+': '+str(e)
    with (OUT/'acquisition_attempt01.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({k:result.get(k) for k in ('fulltext_acquired','http_status','content_type','error','actual_reading_completed')}),flush=True)
    return int(not result['fulltext_acquired'])
if __name__=='__main__':raise SystemExit(main())
