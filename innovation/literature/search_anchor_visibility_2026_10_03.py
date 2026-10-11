"""Sequential bounded public literature query, with raw response provenance."""
import hashlib
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'source_cache/anchor_visibility_search_2026-10-03'
PLAN = ROOT / '2026-10-03_anchor_visibility_literature_plan.md'
QUERIES = {
 'thickness': '(TITLE_ABS:MRI OR TITLE_ABS:"magnetic resonance") AND TITLE_ABS:lesion AND (TITLE_ABS:"slice thickness" OR TITLE_ABS:"partial volume")',
 'acquisition': '(TITLE_ABS:MRI OR TITLE_ABS:"magnetic resonance") AND (TITLE_ABS:"adaptive sampling" OR TITLE_ABS:"active acquisition") AND (TITLE_ABS:lesion OR TITLE_ABS:diagnostic)',
 'interpolation': '(TITLE_ABS:MRI OR TITLE_ABS:"magnetic resonance") AND (TITLE_ABS:"slice interpolation" OR TITLE_ABS:"through-plane") AND TITLE_ABS:lesion',
}
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(exist_ok=False)
    records = []
    for key, query in QUERIES.items():
        row = dict(key=key, query=query, started_utc=datetime.now(timezone.utc).isoformat())
        url = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?' + urllib.parse.urlencode(dict(query=query + ' AND FIRST_PDATE:[1900-01-01 TO 2026-10-03]', format='json', resultType='core', pageSize=15))
        path = OUT / (key + '_attempt_01.response')
        row['url'] = url
        try:
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            with opener.open(urllib.request.Request(url, headers={'User-Agent':'MRI-literature-audit/1.0'}), timeout=30) as response:
                raw = response.read(5000001)
                row.update(http_status=response.status, final_url=response.url)
            path.write_bytes(raw)
            if len(raw) > 5000000:
                raise ValueError('Response exceeds fixed 5MB cap')
            data = json.loads(raw)
            items = data['resultList']['result']
            row.update(reported_total=data['hitCount'], returned=len(items), items=[dict(title=x.get('title'), doi=x.get('doi'), pmid=x.get('id'), pmcid=x.get('pmcid'), year=x.get('pubYear'), abstract=x.get('abstractText'), authors=x.get('authorString'), open_access=x.get('isOpenAccess')) for x in items])
        except Exception as exc:
            row['error'] = type(exc).__name__ + ': ' + str(exc)
        if path.exists():
            row.update(raw_file=path.name, raw_sha256=hashlib.sha256(path.read_bytes()).hexdigest(), bytes=path.stat().st_size)
        row['finished_utc'] = datetime.now(timezone.utc).isoformat()
        records.append(row)
        print(json.dumps({k:row.get(k) for k in ('key','reported_total','returned','error')}), flush=True)
    result = dict(created_utc=datetime.now(timezone.utc).isoformat(), script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), plan_sha256=hashlib.sha256(PLAN.read_bytes()).hexdigest(), scope='title/abstract screening; not full-text reading', responses=records)
    (OUT / 'attempt_01.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
if __name__ == '__main__':
    main()
