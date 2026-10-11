"""Read-only rendering of three original formula pages with existing Poppler."""
import hashlib,json,shutil,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'source_cache/feature_normalization_primary_2026-10-07'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');dest=OUT/'formula_rendering_attempt01.json';assert not dest.exists()
    executable=shutil.which('pdftoppm');assert executable
    rows=[]
    for key,page in [('instance_norm',4),('adaptive_instance_norm',4),('group_norm',6)]:
        pdf=OUT/(key+'.pdf');prefix=OUT/(key+'_formula_page'+str(page));image=prefix.with_suffix('.png');assert not image.exists()
        cmd=[executable,'-f',str(page),'-l',str(page),'-singlefile','-r','120','-png',str(pdf),str(prefix)]
        run=subprocess.run(cmd,capture_output=True,timeout=40,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        assert run.returncode==0 and image.exists(),run.stderr
        rows.append(dict(key=key,pdf_file=pdf.name,pdf_sha256=sha(pdf),page=page,image_file=image.name,
                         image_sha256=sha(image),command=cmd,visual_review_completed=False))
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],script_sha256=sha(__file__),
           executable=executable,executable_sha256=sha(executable),formula_pages=rows,pdfs_modified=False)
    with dest.open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(dict(complete=True,rendered_pages=len(rows))))
if __name__=='__main__':main()
