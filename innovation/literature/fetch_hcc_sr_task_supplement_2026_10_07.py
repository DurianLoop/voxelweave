"""Acquire exact supplement linked by primary JATS; extract by physical page, never by formfeed count."""
import hashlib,json,re,shutil,subprocess,sys,urllib.request,xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/hcc_sr_task_primary_2026-10-07/supplement_attempt01'
XML=OUT.parent/'hcc_sr_task_fulltext.xml'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    links={e.get('{http://www.w3.org/1999/xlink}href') for e in ET.parse(XML).getroot().iter('ext-link') if 'Supplementary' in ' '.join(e.itertext())}
    assert len(links)==1;url=links.pop()
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),source_xml_sha256=sha(XML),url=url,
        fulltext_acquired=False,actual_reading_completed=False,actual_visual_review_completed=False)
    try:
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(url,timeout=25) as response:raw=response.read(25_000_001);r['http_status']=response.status
        assert len(raw)<=25_000_000 and raw.startswith(b'%PDF')
        pdf=OUT/'hcc_sr_task_supplement.pdf';pdf.write_bytes(raw)
        info=subprocess.run([shutil.which('pdfinfo'),str(pdf)],capture_output=True,timeout=20);assert info.returncode==0
        (OUT/'pdfinfo.txt').write_bytes(info.stdout);match=re.search(rb'^Pages:\s+(\d+)',info.stdout,re.M);assert match
        count=int(match.group(1));assert count<=40;pages=[]
        for page in range(1,count+1):
            txt=OUT/f'physical_page_{page:02d}.txt'
            cmd=[shutil.which('pdftotext'),'-f',str(page),'-l',str(page),'-layout','-enc','UTF-8',str(pdf),str(txt)]
            proc=subprocess.run(cmd,capture_output=True,timeout=20);assert proc.returncode==0
            pages.append(dict(page=page,text_file=txt.name,text_sha256=sha(txt),text=txt.read_text(encoding='utf-8')))
        index=OUT/'physical_pages.json';index.write_text(json.dumps(pages,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        r.update(fulltext_acquired=True,physical_pages=count,pdf_file=pdf.name,pdf_sha256=sha(pdf),pages_file=index.name,pages_sha256=sha(index))
    except Exception as e:r['error']=type(e).__name__+': '+str(e)
    with (OUT/'acquisition_attempt01.json').open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(r,ensure_ascii=False),flush=True);return int(not r['fulltext_acquired'])
if __name__=='__main__':raise SystemExit(main())
