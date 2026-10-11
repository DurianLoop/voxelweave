"""Read paper-linked author's visible repository and a commit-pinned README only."""
import json
import re
import sys
from pathlib import Path
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / 'author_attempt01'
sys.path.insert(0, str(ROOT / 'task_routing_author_source_2026_10_08'))
import fetch_author_web_identity as previous


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    previous.client.base.own_priority()
    previous.client.resource_guard()
    OUT.mkdir(exist_ok=False)
    previous.fetcher.OUT = OUT
    rows = [previous.fetcher.get('repository_web', 'https://github.com/ZWang78/MoEDiff-SR', 'html')]
    identity = {}
    if rows[0]['complete']:
        parser = previous.PageParser()
        parser.feed((ROOT / rows[0]['response_binding']['path']).read_text(encoding='utf-8'))
        payload = next((s['payload'] for s in parser.scripts if isinstance(s, dict)
            and isinstance(s.get('payload'), dict) and 'codeViewRepoRoute' in s['payload']), None)
        assert payload is not None, 'Expected GitHub code identity payload absent'
        route = payload['codeViewRepoRoute']
        ref = route['refInfo']
        oid = ref['currentOid']
        assert re.fullmatch(r'[a-f0-9]{40}', oid)
        identity = dict(paper_repository='ZWang78/MoEDiff-SR', current_commit=oid,
            ref_name=ref['name'], root_tree_items=route['tree']['items'],
            complete_recursive_tree_verified=False)
        previous.client.base.new(OUT/'visible_identity.json', identity)
        readmes = [v['path'] for v in identity['root_tree_items']
            if v['contentType']=='file' and v['name'].lower()=='readme.md']
        if len(readmes) == 1:
            rows.append(previous.fetcher.get('README',
                'https://raw.githubusercontent.com/ZWang78/MoEDiff-SR/'+oid+'/'+readmes[0], 'source.txt'))
    receipt = dict(created_utc=datetime.now(timezone.utc).isoformat(),
        complete=all(r['complete'] for r in rows), errors=[e for r in rows for e in r['errors']],
        records=rows, identity=identity, README_read=False, implementation_files_read=0,
        author_code_executed=False, medical_arrays_loaded=0, neural_forwards=0, GPU_forwards=0,
        source_bindings=[previous.client.base.entry(p) for p in [Path(__file__), HERE/'PROTOCOL.md',
            HERE/'primary_attempt02/page_001.txt', ROOT/'task_routing_author_source_2026_10_08/fetch_author_web_identity.py',
            ROOT/'realized_false_positive_task_prior_art_2026_10_08/fetch_mirto_web_fallback.py']],
        resource_snapshot=previous.client.resource_guard())
    previous.client.base.new(OUT/'receipt.json', receipt)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file()) < 6_000_000
    print(json.dumps(receipt, ensure_ascii=False), flush=True)
    return int(not receipt['complete'])


if __name__ == '__main__':
    raise SystemExit(main())
