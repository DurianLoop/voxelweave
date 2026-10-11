"""Focused title/abstract search after the fixed pilot; retain raw responses."""
import hashlib
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'source_cache/task_normalization_context_search_2026-10-03'
QUERIES = [
    'TITLE_ABS:(MRI AND "intensity normalization" AND segmentation)',
    'TITLE_ABS:(MRI AND "normalisation" AND "domain" AND segmentation)',
    'TITLE_ABS:("super-resolution" AND "segmentation" AND "distribution")',
    'TITLE_ABS:(MRI AND "normalization" AND "robustness")',
]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(exist_ok=False)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    report = dict(created_utc=datetime.now(timezone.utc).isoformat(), script_sha256=sha(__file__),
        scope='Title/abstract search only; not paper reading, reproduction, or novelty proof.', responses=[])
    for i, query in enumerate(QUERIES):
        url = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?' + urllib.parse.urlencode(
            dict(query=query, format='json', pageSize=12, resultType='core', sort='RELEVANCE'))
        row = dict(query=query, url=url)
        try:
            with opener.open(urllib.request.Request(url, headers={'User-Agent': 'MRI-literature-audit/1.0'}), timeout=25) as response:
                raw = response.read(8000001)
                row['http_status'] = response.status
            path = OUT / f'query_{i+1:02d}.json'
            path.write_bytes(raw)
            assert len(raw) <= 8000000
            parsed = json.loads(raw)
            row.update(raw_file=path.name, raw_sha256=sha(path), hit_count=parsed['hitCount'],
                items=[{k: x.get(k) for k in ('title', 'authorString', 'pubYear', 'doi', 'pmcid', 'id', 'source', 'isOpenAccess', 'abstractText')}
                    for x in parsed['resultList']['result']])
        except Exception as exc:
            row['error'] = type(exc).__name__ + ': ' + str(exc)
        report['responses'].append(row)
        (OUT / 'attempt_01.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(dict(query=query, hit_count=row.get('hit_count'), error=row.get('error'),
            titles=[{k: x[k] for k in ('title', 'doi', 'pmcid', 'pubYear')} for x in row.get('items', [])]), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
