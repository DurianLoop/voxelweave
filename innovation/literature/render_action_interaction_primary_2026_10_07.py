"""Render three selected primary PDF pages with installed Poppler; not paper reproduction."""
import concurrent.futures,hashlib,json,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'literature/source_cache/action_interaction_primary_2026-10-07'
def render(item):
    key,page=item;prefix=OUT/(key+f'_page{page:02d}_render')
    png=prefix.with_suffix('.png');assert not png.exists()
    proc=subprocess.run([shutil.which('pdftoppm'),'-f',str(page),'-l',str(page),'-singlefile','-scale-to','1600','-png',str(OUT/(key+'.pdf')),str(prefix)],capture_output=True,timeout=30)
    assert proc.returncode==0 and png.exists()
    return dict(key=key,page=page,render_exit=proc.returncode,file=png.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(png.read_bytes()).hexdigest(),visual_review_performed=False)
def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(render,[('compressive_mri_verified',5),('adaptive_submodularity',6),('scalable_mri_verified',8)]))
    p=OUT/'render_attempt01.json';assert not p.exists();p.write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8');print(json.dumps(rows));return 0
if __name__=='__main__':raise SystemExit(main())
