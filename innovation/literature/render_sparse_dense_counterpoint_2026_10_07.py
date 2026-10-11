"""Render mask saturation and direct semantic task evidence."""
import hashlib,json,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'literature/source_cache/sparse_dense_counterpoint_2026-10-07'
def main():
    rows=[]
    for page in (3,7):
        prefix=OUT/f'page{page:02d}_render';png=prefix.with_suffix('.png');assert not png.exists()
        p=subprocess.run([shutil.which('pdftoppm'),'-f',str(page),'-l',str(page),'-singlefile','-scale-to','1600','-png',str(OUT/'jaritz_sparse_dense.pdf'),str(prefix)],capture_output=True,timeout=30)
        assert p.returncode==0 and png.exists()
        rows.append(dict(page=page,file=png.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(png.read_bytes()).hexdigest(),render_exit=0,visual_review_performed=False))
    with (OUT/'render_attempt01.json').open('x',encoding='utf-8') as f:json.dump(rows,f,indent=2)
    print(json.dumps(rows));return 0
if __name__=='__main__':raise SystemExit(main())
