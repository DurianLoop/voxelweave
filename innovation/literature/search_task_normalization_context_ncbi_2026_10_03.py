"""Narrow PMC title/abstract fallback after Europe PMC HTTP503 failures."""
import hashlib
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'source_cache/task_normalization_context_ncbi_2026-10-03'
QUERIES = [
    '("intensity normalization"[Title/Abstract] OR "intensity normalisation"[Title/Abstract]) AND (MRI[Title/Abstract] OR "magnetic resonance"[Title/Abstract]) AND segmentation[Title/Abstract]',
    '(normalization[Title/Abstract] OR normalisation[Title/Abstract]) AND "deep learning"[Title/Abstract] AND MRI[Title/Abstract] AND robustness[Title/Abstract]',
    '"super-resolution"[Title/Abstract] AND segmentation[Title/Abstract] AND ("domain shift"[Title/Abstract] OR "distribution shift"[Title/Abstract])',
]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(exist_ok=False)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    report = dict(created_utc=datetime.now(timezone.utc).isoformat(), script_sha256=sha(__file__),
        scope='Title/abstract indexed discovery only, bounded date; no fulltext reading claims.', responses=[])
    for i, query in enumerate(QUERIES):
        row = dict(query=query)
        try:
            url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?' + urllib.parse.urlencode(
                dict(db='pmc', term='(' + query + ') AND ("1900/01/01"[Publication Date] : "2026/10/03"[Publication Date])',
                     retmode='json', retmax=12, sort='relevance'))
            row['url'] = url
            with opener.open(url, timeout=25) as response:
                raw = response.read(4000001)
            path = OUT / f'query_{i+1:02d}.response'
            path.write_bytes(raw)
            search = json.loads(raw)['esearchresult']
            row.update(raw_file=path.name, raw_sha256=sha(path), hit_count=int(search['count']), pmc_ids=search['idlist'])
            if search['idlist']:
                url2 = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?' + urllib.parse.urlencode(
                    dict(db='pmc', id=','.join(search['idlist']), retmode='json'))
                with opener.open(url2, timeout=25) as response:
                    raw2 = response.read(4000001)
                path2 = OUT / f'summary_{i+1:02d}.response'
                path2.write_bytes(raw2)
                summary = json.loads(raw2)['result']
                row.update(summary_url=url2, summary_file=path2.name, summary_sha256=sha(path2),
                    items=[dict(pmcid='PMC'+k, title=summary[k]['title'], pubdate=summary[k]['pubdate'],
                        articleids=summary[k].get('articleids', [])) for k in summary['uids']])
        except Exception as exc:
            row['error'] = type(exc).__name__ + ': ' + str(exc)
        report['responses'].append(row)
        (OUT / 'attempt_01.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(row, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
