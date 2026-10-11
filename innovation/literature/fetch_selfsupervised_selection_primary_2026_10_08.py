"""Public author PDFs; acquisition does not constitute reading."""
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'literature/source_cache/selfsupervised_selection_primary_2026-10-08'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True, exist_ok=False)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    rows = []
    for key, url in [('noise2self','https://arxiv.org/pdf/1901.11365'), ('ssdu','https://arxiv.org/pdf/1912.07669')]:
        start = time.perf_counter()
        row = dict(key=key, requested_url=url, complete=False, errors=[], new_paper_read=False)
        try:
            with opener.open(urllib.request.Request(url, headers={'User-Agent':'MRI-public-literature/1.0'}), timeout=25) as response:
                data = response.read(32_000_001)
                assert len(data) <= 32_000_000 and data.startswith(b'%PDF')
                row['response'] = dict(final_url=response.geturl(), http_status=response.status,
                    content_type=response.headers.get('Content-Type'), bytes=len(data))
            p = OUT/(key+'.pdf')
            p.write_bytes(data)
            info = subprocess.run([shutil.which('pdfinfo'), str(p)], capture_output=True, timeout=30)
            assert info.returncode == 0
            (OUT/(key+'_pdfinfo.txt')).write_bytes(info.stdout+info.stderr)
            pages = int(re.search(rb'^Pages:\s+(\d+)', info.stdout, re.M)[1])
            texts = []
            for page in range(1,pages+1):
                dest = OUT/f'{key}_page{page:02d}.txt'
                proc = subprocess.run([shutil.which('pdftotext'),'-f',str(page),'-l',str(page),'-layout','-enc','UTF-8',str(p),str(dest)], capture_output=True, timeout=30)
                assert proc.returncode == 0
                texts.append(dict(physical_page=page, path=dest.relative_to(ROOT).as_posix(), sha256=sha(dest), characters=len(dest.read_text(encoding='utf-8')), extraction_exit=proc.returncode))
            row.update(complete=True, PDF=dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p), bytes=p.stat().st_size), physical_pages=pages, page_texts=texts)
        except Exception as error:
            row['errors'].append(type(error).__name__+': '+str(error))
        row['elapsed_seconds'] = time.perf_counter()-start
        rows.append(row)
    receipt = dict(created_utc=datetime.now(timezone.utc).isoformat(), script_sha256=sha(__file__), public_GET_only=True, new_primary_papers_read=0, records=rows)
    with (OUT/'acquisition_attempt01.json').open('x',encoding='utf-8') as f:
        json.dump(receipt,f,ensure_ascii=False,indent=2)
        f.write('\n')
    print(json.dumps([{k:r.get(k) for k in ('key','complete','physical_pages','errors')} for r in rows]),flush=True)
    return int(not all(r['complete'] for r in rows))


if __name__ == '__main__':
    raise SystemExit(main())
