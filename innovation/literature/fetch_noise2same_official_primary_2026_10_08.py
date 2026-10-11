"""Acquire two public author PDFs. Download and extraction are not reading."""
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
OUT = ROOT/'literature/source_cache/blindspot_dependence_primary_2026-10-08/noise2same_official_attempt01'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True, exist_ok=False)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    records = []
    for key, url in (('noise2same_verified', 'https://proceedings.neurips.cc/paper_files/paper/2020/file/ea6b2efbdd4255a9f1b3bbc6399b58f4-Paper.pdf'),):
        started = time.perf_counter()
        row = dict(key=key, requested_url=url, complete=False, errors=[], new_paper_read=False)
        try:
            with opener.open(urllib.request.Request(url, headers={'User-Agent':'MRI-public-literature/1.0'}), timeout=30) as response:
                data = response.read(8_000_001)
                assert len(data) <= 8_000_000 and data.startswith(b'%PDF')
                row['response'] = dict(final_url=response.geturl(), http_status=response.status,
                                       content_type=response.headers.get('Content-Type'), bytes=len(data))
            p = OUT/(key+'.pdf')
            with p.open('xb') as f:
                f.write(data)
            info = subprocess.run([shutil.which('pdfinfo'), str(p)], capture_output=True, timeout=30)
            assert info.returncode == 0
            (OUT/(key+'_pdfinfo.txt')).write_bytes(info.stdout+info.stderr)
            pages = int(re.search(rb'^Pages:\s+(\d+)', info.stdout, re.M)[1])
            texts = []
            for page in range(1, pages+1):
                dest = OUT/f'{key}_page{page:02d}.txt'
                result = subprocess.run([shutil.which('pdftotext'), '-f', str(page), '-l', str(page),
                                         '-layout', '-enc', 'UTF-8', str(p), str(dest)], capture_output=True, timeout=30)
                assert result.returncode == 0
                texts.append(dict(physical_page=page, path=dest.relative_to(ROOT).as_posix(), sha256=sha(dest),
                                  characters=len(dest.read_text(encoding='utf-8')), extraction_exit=0))
            row.update(complete=True, physical_pages=pages, page_texts=texts,
                       PDF=dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p), bytes=p.stat().st_size))
        except Exception as exc:
            row['errors'].append(type(exc).__name__+': '+str(exc))
        row['elapsed_seconds'] = time.perf_counter()-started
        records.append(row)
    receipt = dict(created_utc=datetime.now(timezone.utc).isoformat(), script_sha256=sha(__file__),
                   protocol_sha256=sha(ROOT/'literature/BLINDSPOT_PRIMARY_IDENTITY_CORRECTION_2026-10-08.md'),
                   public_GET_only=True, new_primary_papers_read=0, records=records)
    with (OUT/'acquisition_attempt01.json').open('x', encoding='utf-8') as f:
        json.dump(receipt, f, ensure_ascii=False, indent=2)
        f.write('\n')
    assert sum(p.stat().st_size for p in OUT.iterdir() if p.is_file()) < 20_000_000
    print(json.dumps([{k:r.get(k) for k in ('key', 'complete', 'physical_pages', 'errors')} for r in records]), flush=True)
    return int(not all(r['complete'] for r in records))


if __name__ == '__main__':
    raise SystemExit(main())
