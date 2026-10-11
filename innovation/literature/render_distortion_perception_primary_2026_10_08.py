"""Render four actually selected definition/theorem pages; not a visual-review receipt."""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'literature/source_cache/distortion_perception_primary_2026-10-08'


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    records = []
    for key, pages in (('perception_distortion', [3, 5]), ('rate_distortion_perception', [3, 5])):
        for page in pages:
            prefix = OUT/f'{key}_page{page:02d}_visual'
            assert not prefix.with_suffix('.png').exists()
            result = subprocess.run([shutil.which('pdftoppm'), '-f', str(page), '-l', str(page),
                                     '-singlefile', '-scale-to', '1400', '-png', str(OUT/(key+'.pdf')), str(prefix)],
                                    capture_output=True, timeout=45)
            assert result.returncode == 0
            p = prefix.with_suffix('.png')
            records.append(dict(key=key, physical_page=page, path=p.relative_to(ROOT).as_posix(),
                                bytes=p.stat().st_size, sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                                actual_subprocess_exit=0, visually_reviewed=False))
    with (OUT/'render_attempt01.json').open('x', encoding='utf-8') as f:
        json.dump(dict(complete=True, errors=[], records=records), f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(json.dumps(dict(complete=True, rendered_pages=len(records), rendered_bytes=sum(v['bytes'] for v in records))), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
