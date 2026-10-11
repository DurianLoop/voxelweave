"""Render method, sparsity comparison, fusion, and correlation pages for actual visual review."""
import concurrent.futures,hashlib,json,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/direct_observed_primary_2026-10-07'
def render(item):
    key,page=item;prefix=OUT/(key+f'_page{page:02d}_render');png=prefix.with_suffix('.png');assert not png.exists()
    proc=subprocess.run([shutil.which('pdftoppm'),'-f',str(page),'-l',str(page),'-singlefile','-scale-to','1600','-png',str(OUT/(key+'.pdf')),str(prefix)],capture_output=True,timeout=30)
    assert proc.returncode==0 and png.exists()
    return dict(key=key,page=page,file=png.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(png.read_bytes()).hexdigest(),render_exit=0,visual_review_performed=False)
def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        rows=list(pool.map(render,[('sparsity_invariant',6),('confidence_propagation',4),('confidence_propagation',7),('confidence_propagation',13)]))
    with (OUT/'render_attempt01.json').open('x',encoding='utf-8') as f:json.dump(rows,f,indent=2)
    print(json.dumps(rows));return 0
if __name__=='__main__':raise SystemExit(main())
