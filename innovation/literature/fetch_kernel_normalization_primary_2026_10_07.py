"""Get fixed arXiv paper versions, extract every page, record no reading claim."""
import hashlib,json,shutil,subprocess,sys,urllib.request
from datetime import datetime,timezone
from pathlib import Path
OUT=Path(__file__).resolve().parent/'source_cache/kernel_normalization_primary_2026-10-07'
REQUESTS=[('kin','https://arxiv.org/pdf/2208.10730v1'),('kernel_norm','https://arxiv.org/pdf/2205.10089v4')]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}));rows=[]
    for key,url in REQUESTS:
        row=dict(key=key,url=url,fulltext_acquired=False,actual_reading_completed=False)
        try:
            with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRI-literature-audit/1.0'}),timeout=25) as resp:
                raw=resp.read(15_000_001);row.update(http_status=resp.status,final_url=resp.url)
            assert len(raw)<=15_000_000 and raw.startswith(b'%PDF');pdf=OUT/(key+'.pdf');pdf.write_bytes(raw)
            txt=OUT/(key+'_layout.txt');cmd=[shutil.which('pdftotext'),'-layout','-enc','UTF-8',str(pdf),str(txt)]
            run=subprocess.run(cmd,capture_output=True,timeout=35);assert run.returncode==0,run.stderr
            pages=txt.read_text(encoding='utf-8').split('\f')
            if not pages[-1].strip():pages.pop()
            pagefile=OUT/(key+'_pages.json');pagefile.write_text(json.dumps([dict(page=i+1,text=t) for i,t in enumerate(pages)],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            row.update(fulltext_acquired=True,pdf_file=pdf.name,pdf_sha256=sha(pdf),pages=len(pages),
                       text_file=txt.name,text_sha256=sha(txt),pages_file=pagefile.name,pages_sha256=sha(pagefile),
                       extraction_command=cmd,first_page_preview=pages[0][:700])
        except Exception as e:row['error']=type(e).__name__+': '+str(e)
        rows.append(row);r=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),papers=rows,actual_reading_completed=False)
        (OUT/'acquisition_attempt01.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(row,ensure_ascii=False),flush=True)
    return int(not all(row['fulltext_acquired'] for row in rows))
if __name__=='__main__':raise SystemExit(main())
