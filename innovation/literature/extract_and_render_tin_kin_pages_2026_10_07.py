"""Correct TIN page indexing via physical PDF pages; render original formula/table pages."""
import hashlib,json,re,shutil,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
BASE=Path(__file__).resolve().parent/'source_cache'
OUT=BASE/'tile_context_visual_review_2026-10-07'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    tin=BASE/'thumbnail_instance_normalization_v2_2026-10-07/thumbnail_instance_norm.pdf'
    kin=BASE/'kernel_normalization_primary_2026-10-07/kin.pdf'
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),
        actual_visual_review_completed=False,rendered=[],tin_page_extraction={})
    run=subprocess.run([shutil.which('pdfinfo'),str(tin)],capture_output=True,timeout=15)
    text=run.stdout.decode('utf-8',errors='replace');assert run.returncode==0
    info=OUT/'tin_pdfinfo.stdout.txt';info.write_text(text,encoding='utf-8')
    pages=int(re.search(r'^Pages:\s+(\d+)',text,re.M).group(1));assert pages==10
    records=[]
    for page in range(1,pages+1):
        txt=OUT/f'tin_physical_page_{page:02d}.txt'
        command=[shutil.which('pdftotext'),'-f',str(page),'-l',str(page),'-layout','-enc','UTF-8',str(tin),str(txt)]
        result=subprocess.run(command,capture_output=True,timeout=20);assert result.returncode==0,result.stderr
        records.append(dict(page=page,text=txt.read_text(encoding='utf-8').rstrip('\f'),text_file=txt.name,text_sha256=sha(txt)))
    pagefile=OUT/'tin_physical_pages.json';pagefile.write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    r['tin_page_extraction']=dict(physical_pages=pages,previous_formfeed_segments=12,
        diagnosis='PDF chart font includes formfeed codepoints; splitting pdftotext output by formfeed overcounts physical pages.',
        old_extraction_preserved=True,page_file=pagefile.name,page_sha256=sha(pagefile),source_pdf_sha256=sha(tin))
    for key,pdf,page in [('tin_formula',tin,4),('kin_formula',kin,7),('kin_glioma_table',kin,12),('kin_downstream',kin,18)]:
        prefix=OUT/key;cmd=[shutil.which('pdftoppm'),'-f',str(page),'-l',str(page),'-r','120','-singlefile','-png',str(pdf),str(prefix)]
        result=subprocess.run(cmd,capture_output=True,timeout=40);assert result.returncode==0,result.stderr
        image=prefix.with_suffix('.png');assert image.exists()
        r['rendered'].append(dict(key=key,source_pdf=str(pdf),source_pdf_sha256=sha(pdf),physical_page=page,
            png_file=image.name,png_sha256=sha(image),command=cmd,actual_visual_review_completed=False))
    (OUT/'extraction_and_render_attempt01.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(tin_physical_pages=pages,rendered_pages=len(r['rendered']),actual_visual_review_completed=False)))
if __name__=='__main__':main()
