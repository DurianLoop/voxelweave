"""Archive fixed narrow metadata searches; never equates acquisition with reading."""
import hashlib, json, sys, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path
OUT = Path(__file__).resolve().parent / 'source_cache/tile_context_primary_2026-10-07'
QUERIES = [
    ('norm_patch', 'TITLE_ABS:segmentation AND TITLE_ABS:normalization AND TITLE_ABS:patch'),
    ('tiling_artifact', 'TITLE_ABS:segmentation AND TITLE_ABS:tiling AND TITLE_ABS:artifact'),
    ('exact_tile', 'TITLE_ABS:"tile-based" AND TITLE_ABS:inference'),
]
def main():
    sys.stdout.reconfigure(encoding='utf-8'); OUT.mkdir(exist_ok=False)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    report = dict(created_utc=datetime.now(timezone.utc).isoformat(), actual_reading_completed=False,
                  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), queries=[])
    for key, query in QUERIES:
        url = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?' + urllib.parse.urlencode(
            dict(query=query, format='json', resultType='core', pageSize=8))
        row = dict(key=key, query=query, url=url, complete=False)
        try:
            with opener.open(url, timeout=18) as response:
                raw = response.read(5_000_001); row['http_status'] = response.status
            path = OUT / (key + '_attempt01.response'); path.write_bytes(raw)
            assert len(raw) <= 5_000_000
            data = json.loads(raw); items = data['resultList']['result']
            row.update(complete=True, hit_count=data['hitCount'], returned=len(items), raw_file=path.name,
                       raw_sha256=hashlib.sha256(raw).hexdigest(), items=[
                           {k:x.get(k) for k in ('title','authorString','doi','pmcid','pubYear','id','source',
                            'isOpenAccess','fullTextUrlList','abstractText')} for x in items])
        except Exception as e:
            row['error'] = type(e).__name__ + ': ' + str(e)
        report['queries'].append(row)
        (OUT / 'search_attempt01.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        print(json.dumps(row, ensure_ascii=False), flush=True)
    return int(any(not row['complete'] for row in report['queries']))
if __name__ == '__main__':
    raise SystemExit(main())
