"""Render selected original pages; this records rendering, not visual reading."""
import hashlib,json,shutil,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PDF=ROOT/'literature/source_cache/learn_then_test_primary_2026-10-07/learn_then_test.pdf'
OUT=ROOT/'literature/source_cache/learn_then_test_render_2026-10-07'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);rows=[]
    for page in (4,5,6,14,15):
        prefix=OUT/f'page{page:02d}'
        q=subprocess.run([shutil.which('pdftoppm'),'-f',str(page),'-l',str(page),'-singlefile','-scale-to','1700','-png',str(PDF),str(prefix)],capture_output=True,timeout=30)
        assert q.returncode==0 and prefix.with_suffix('.png').is_file()
        png=prefix.with_suffix('.png')
        rows.append(dict(page=page,file=png.relative_to(ROOT).as_posix(),sha256=sha(png),render_exit=0,visual_review_performed=False))
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,script_sha256=sha(__file__),
        pdf_file=PDF.relative_to(ROOT).as_posix(),pdf_sha256=sha(PDF),records=rows)
    with (OUT/'render_attempt01.json').open('x',encoding='utf-8') as s:json.dump(r,s,indent=2);s.write('\n')
    print(json.dumps(dict(complete=True,pages_rendered=len(rows))));return 0
if __name__=='__main__':raise SystemExit(main())
