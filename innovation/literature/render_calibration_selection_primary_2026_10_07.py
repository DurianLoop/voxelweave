"""Render fixed methods/results pages; actual viewing is recorded separately."""
import concurrent.futures, hashlib, json, shutil, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/calibration_selection_render_2026-10-07'
PRIMARY=ROOT/'literature/source_cache/calibration_selection_primary_2026-10-07'
RECOVERY=ROOT/'literature/source_cache/calibration_selection_pmlr_attempt02_2026-10-07'
ITEMS=[('calibration',6),('calibration',8),('selectivenet',3),('selectivenet',6),
       ('conformal_risk',3),('conformal_risk',5),('conformal_risk',6)]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def render(item):
    key,page=item;pdf=(PRIMARY if key=='conformal_risk' else RECOVERY)/(key+'.pdf')
    prefix=OUT/(key+f'_page{page:02d}');p=prefix.with_suffix('.png')
    q=subprocess.run([shutil.which('pdftoppm'),'-f',str(page),'-l',str(page),'-singlefile','-scale-to','1600','-png',str(pdf),str(prefix)],capture_output=True,timeout=30)
    assert q.returncode==0 and p.is_file()
    return dict(key=key,page=page,file=p.relative_to(ROOT).as_posix(),sha256=sha(p),pdf_file=pdf.relative_to(ROOT).as_posix(),
                pdf_sha256=sha(pdf),render_exit=0,visual_review_performed=False)
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(render,ITEMS))
    with (OUT/'render_attempt01.json').open('x',encoding='utf-8') as f:
        json.dump(dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,script_sha256=sha(__file__),records=rows),f,indent=2);f.write('\n')
    print(json.dumps(dict(complete=True,rendered_pages=len(rows))));return 0
if __name__=='__main__':raise SystemExit(main())

