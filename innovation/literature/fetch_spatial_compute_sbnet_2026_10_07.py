"""One prespecified citation follow-up, using frozen acquisition implementation."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
import fetch_spatial_compute_primary_2026_10_07 as acquisition
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/spatial_compute_sbnet_2026-10-07'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(parents=True,exist_ok=False)
    source=Path(acquisition.__file__);(OUT/(source.name+'.source_snapshot')).write_bytes(source.read_bytes());acquisition.OUT=OUT
    row=acquisition.acquire(('sbnet','https://openaccess.thecvf.com/content_cvpr_2018/html/Ren_SBNet_Sparse_Blocks_CVPR_2018_paper.html'))
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),public_GET_only=True,new_primary_papers_read=0,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in (Path(__file__),source,ROOT/'literature/2026-10-07_spatial_compute_sbnet_selection_addendum.md')],records=[row])
    (OUT/'acquisition_attempt01.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:row.get(k) for k in ('key','complete','physical_pages','pdf_bytes','errors')}),flush=True);return int(not row['complete'])
if __name__=='__main__':raise SystemExit(main())
