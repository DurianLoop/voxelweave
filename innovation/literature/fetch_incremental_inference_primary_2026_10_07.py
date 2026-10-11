"""Public read-only acquisition; no system proxy, environment or training changes."""
import concurrent.futures, hashlib, json, re, shutil, subprocess, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'literature/source_cache/incremental_inference_primary_2026-10-07'
LIMIT = 32_000_000

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def acquire(job):
    key, url = job
    r = dict(key=key, requested_url=url, candidate_identity_not_yet_verified=True, complete=False, errors=[])
    started = time.perf_counter()
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        req = urllib.request.Request(url, headers={'User-Agent': 'MRI-literature-reading/1.0'})
        with opener.open(req, timeout=25) as response:
            raw = response.read(LIMIT+1)
            r.update(final_url=response.geturl(), http_status=response.status,
                     content_type=response.headers.get('Content-Type'), bytes=len(raw))
        assert len(raw) <= LIMIT
        if raw.startswith(b'%PDF'):
            pdf = OUT / (key+'.pdf')
            pdf.write_bytes(raw)
        else:
            page = OUT / (key+'_landing.html')
            page.write_bytes(raw)
            r.update(landing_file=page.relative_to(ROOT).as_posix(), landing_sha256=sha(page))
            html = raw.decode('utf-8', errors='replace')
            links = re.findall(r'href=[\"\']([^\"\']+\.pdf)[\"\']', html)
            links = [urllib.parse.urljoin(url, link) for link in links if '/papers/' in link or '/content/' in link]
            assert links, 'No official PDF link in candidate landing page'
            pdfurl = links[0]
            req = urllib.request.Request(pdfurl, headers={'User-Agent': 'MRI-literature-reading/1.0'})
            with opener.open(req, timeout=25) as response:
                raw = response.read(LIMIT+1)
                r.update(pdf_requested_url=pdfurl, pdf_final_url=response.geturl(), pdf_http_status=response.status)
            assert len(raw) <= LIMIT and raw.startswith(b'%PDF')
            pdf = OUT / (key+'.pdf'); pdf.write_bytes(raw)
        r.update(pdf_file=pdf.relative_to(ROOT).as_posix(), pdf_sha256=sha(pdf), pdf_bytes=pdf.stat().st_size)
        info = subprocess.run([shutil.which('pdfinfo'), str(pdf)], capture_output=True, timeout=30)
        (OUT/(key+'_pdfinfo.txt')).write_bytes(info.stdout+info.stderr)
        r['pdfinfo_exit'] = info.returncode
        assert info.returncode == 0
        match = re.search(rb'^Pages:\s+(\d+)', info.stdout, flags=re.M)
        assert match
        pages = int(match[1]); r['physical_pages'] = pages
        records = []
        for p in range(1, pages+1):
            txt = OUT / (key+f'_page{p:02d}.txt')
            command = [shutil.which('pdftotext'), '-f', str(p), '-l', str(p), '-layout', '-enc', 'UTF-8', str(pdf), str(txt)]
            result = subprocess.run(command, capture_output=True, timeout=30)
            assert result.returncode == 0 and txt.is_file(), result.stderr.decode(errors='replace')
            records.append(dict(physical_page=p, text_file=txt.relative_to(ROOT).as_posix(), text_sha256=sha(txt),
                                extraction_exit=result.returncode, characters=len(txt.read_text(encoding='utf-8'))))
        r.update(page_texts=records, complete=True, new_paper_read=False, actual_pages_read=[])
    except Exception as e:
        r['errors'].append(type(e).__name__+': '+str(e))
    r['elapsed_seconds'] = time.perf_counter()-started
    return r

def main():
    OUT.mkdir(exist_ok=False, parents=True)
    jobs = [
        ('deltacnn', 'https://openaccess.thecvf.com/content/CVPR2022/html/Parger_DeltaCNN_End-to-End_CNN_Inference_of_Sparse_Frame_Differences_in_Videos_CVPR_2022_paper.html'),
        ('sige', 'https://arxiv.org/pdf/2211.02048'),
        ('deepcache', 'https://arxiv.org/pdf/2312.00858'),
    ]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(acquire, jobs))
    receipt = dict(created_utc=datetime.now(timezone.utc).isoformat(), script_sha256=sha(__file__),
                   public_GET_only=True, system_proxy_unchanged=True, raw_response_limit_bytes=LIMIT,
                   no_GPU_or_MRI_access=True, new_papers_read=0, records=results)
    (OUT/'acquisition_attempt01.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps([{k:r.get(k) for k in ('key','complete','physical_pages','pdf_bytes','errors')} for r in results]), flush=True)
    return int(not all(r['complete'] for r in results))

if __name__ == '__main__':
    raise SystemExit(main())
