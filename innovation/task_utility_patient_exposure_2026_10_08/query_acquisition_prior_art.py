"""Bounded public index GETs; retain successes and failures without retries."""
import hashlib, json, subprocess, sys, time, traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / 'index_attempt01'

def entry(path):
    return dict(path=path.relative_to(ROOT).as_posix(), bytes=path.stat().st_size,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest())

def fetch(job):
    key, query = job
    url = 'https://export.arxiv.org/api/query?' + urlencode(dict(search_query=query, start=0, max_results=8))
    row = dict(key=key, query=query, requested_url=url, complete=False, errors=[])
    tick = time.perf_counter()
    try:
        path = OUT / (key + '.xml')
        proc = subprocess.run(['curl.exe', '--noproxy', '*', '--fail', '--silent', '--show-error',
            '--location', '--max-redirs', '3', '--proto', '=https', '--proto-redir', '=https',
            '--max-time', '30', '--max-filesize', '3000000', '--dump-header', str(OUT/(key+'_headers.txt')),
            '--output', str(path), '--write-out', '%{http_code}\n%{url_effective}', url],
            capture_output=True, timeout=35)
        (OUT/(key+'_stderr.txt')).write_bytes(proc.stderr)
        row.update(curl_exit=proc.returncode, status_and_effective_url=proc.stdout.decode('utf-8', errors='replace'))
        if proc.returncode:
            raise RuntimeError(proc.stderr.decode('utf-8', errors='replace'))
        assert path.stat().st_size <= 3_000_000
        data = ET.fromstring(path.read_bytes())
        ns = {'a':'http://www.w3.org/2005/Atom', 'o':'http://a9.com/-/spec/opensearch/1.1/'}
        row['total_results'] = data.findtext('o:totalResults', namespaces=ns)
        row['entries'] = [dict(id=e.findtext('a:id', namespaces=ns),
            title=' '.join((e.findtext('a:title', namespaces=ns) or '').split()),
            published=e.findtext('a:published', namespaces=ns), updated=e.findtext('a:updated', namespaces=ns),
            authors=[a.findtext('a:name', namespaces=ns) for a in e.findall('a:author', ns)],
            summary=e.findtext('a:summary', namespaces=ns),
            links=[dict(v.attrib) for v in e.findall('a:link', ns)]) for e in data.findall('a:entry', ns)]
        row.update(file=entry(path), complete=True)
    except Exception as exc:
        row['errors'].append(type(exc).__name__+': '+str(exc))
        row['traceback'] = traceback.format_exc()
    row['elapsed_seconds'] = time.perf_counter()-tick
    return row

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(exist_ok=False)
    jobs = [('tackle', 'ti:TACKLE AND (all:MRI OR all:"magnetic resonance")'),
            ('active_acquisition', 'ti:"Active Acquisition for Magnetic Resonance Imaging"'),
            ('task_aware_acquisition', '(ti:"task-aware" OR ti:"task-driven") AND (ti:acquisition OR ti:sampling) AND (all:MRI OR all:"magnetic resonance")')]
    with ThreadPoolExecutor(max_workers=3) as pool:
        rows = list(pool.map(fetch, jobs))
    result = dict(created_utc=datetime.now(timezone.utc).isoformat(), complete=all(r['complete'] for r in rows),
        records=rows, public_GET_only=True, TLS_verification_disabled=False, retry_count=0,
        source_bindings=[entry(Path(__file__)), entry(HERE/'PROTOCOL.md')],
        new_papers_read=0, medical_arrays_loaded=0, neural_forwards=0, GPU_forwards=0, training_updates=0)
    with (OUT/'receipt.json').open('x', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2); f.write('\n')
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return int(not result['complete'])

if __name__ == '__main__':
    raise SystemExit(main())
