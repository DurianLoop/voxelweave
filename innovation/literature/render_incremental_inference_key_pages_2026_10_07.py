"""Read-only rendering of three primary method pages with existing Poppler."""
import hashlib,json,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/incremental_inference_key_page_renders_2026-10-07'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    OUT.mkdir(exist_ok=False,parents=True);records=[]
    for key,pdf,page in (
        ('deltacnn','incremental_inference_primary_2026-10-07/deltacnn.pdf',4),
        ('sige','incremental_inference_primary_2026-10-07/sige.pdf',4),
        ('deepcache','deepcache_cvpr_alternate_2026-10-07/deepcache_cvpr.pdf',5)):
        source=ROOT/'literature/source_cache'/pdf;prefix=OUT/(key+f'_physical_page{page:02d}')
        command=[shutil.which('pdftoppm'),'-f',str(page),'-l',str(page),'-r','130','-singlefile','-png',str(source),str(prefix)]
        r=subprocess.run(command,capture_output=True,timeout=45)
        (OUT/(key+'_render_stderr.txt')).write_bytes(r.stderr)
        image=prefix.with_suffix('.png')
        records.append(dict(key=key,physical_page=page,pdf_sha256=sha(source),tool_exit=r.returncode,
            image_file=image.relative_to(ROOT).as_posix() if image.exists() else None,
            image_sha256=sha(image) if image.exists() else None,visually_reviewed=False))
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),read_only=True,
        existing_render_tool=shutil.which('pdftoppm'),records=records,
        complete=all(r['tool_exit']==0 and r['image_file'] for r in records))
    (OUT/'render_attempt01.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result),flush=True);return int(not result['complete'])
if __name__=='__main__':raise SystemExit(main())
