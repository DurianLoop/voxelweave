"""Acquire three primary normalization papers; downloading is not a reading claim."""
import hashlib,json,sys,urllib.request,subprocess,shutil
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'source_cache/feature_normalization_primary_2026-10-07'
REQUESTS=[
 ('instance_norm','https://arxiv.org/pdf/1607.08022'),
 ('adaptive_instance_norm','https://openaccess.thecvf.com/content_ICCV_2017/papers/Huang_Arbitrary_Style_Transfer_ICCV_2017_paper.pdf'),
 ('group_norm','https://openaccess.thecvf.com/content_ECCV_2018/papers/Yuxin_Wu_Group_Normalization_ECCV_2018_paper.pdf')]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    pdftotext=shutil.which('pdftotext');assert pdftotext
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}));rows=[]
    for key,url in REQUESTS:
        row=dict(key=key,url=url,fulltext_acquired=False,actual_reading_completed=False)
        try:
            with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRI-literature-audit/1.0'}),timeout=30) as resp:
                raw=resp.read(12_000_001);row.update(http_status=resp.status,final_url=resp.url)
            assert len(raw)<=12_000_000 and raw.startswith(b'%PDF')
            pdf=OUT/(key+'.pdf');pdf.write_bytes(raw)
            txt=OUT/(key+'_layout.txt');cmd=[pdftotext,'-layout','-enc','UTF-8',str(pdf),str(txt)]
            run=subprocess.run(cmd,capture_output=True,timeout=40,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            assert run.returncode==0,run.stderr
            pages=txt.read_text(encoding='utf-8').split('\f')
            if not pages[-1].strip():pages.pop()
            pagepath=OUT/(key+'_pages.json')
            pagepath.write_text(json.dumps([dict(page=i+1,text=t) for i,t in enumerate(pages)],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            row.update(fulltext_acquired=True,bytes=len(raw),pages=len(pages),pdf_file=pdf.name,pdf_sha256=sha(pdf),
                       text_file=txt.name,text_sha256=sha(txt),page_text_file=pagepath.name,page_text_sha256=sha(pagepath),
                       extraction_command=cmd,first_page_preview=pages[0][:260])
        except Exception as e:row['error']=type(e).__name__+': '+str(e)
        rows.append(row)
        record=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),papers=rows,
                    primary_source_scope='Public original arXiv/CVF PDFs. Acquisition and extraction only.',
                    root_environment_modified=False)
        (OUT/'acquisition_attempt01.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:row.get(k) for k in ('key','fulltext_acquired','pages','first_page_preview','error')},ensure_ascii=False),flush=True)
    return int(not all(r['fulltext_acquired'] for r in rows))
if __name__=='__main__':raise SystemExit(main())
