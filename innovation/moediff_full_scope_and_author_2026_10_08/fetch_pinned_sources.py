"""Save actual visible author Python files as text; never import or execute them."""
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE/'sources_attempt01'
sys.path.insert(0, str(ROOT/'task_routing_author_source_2026_10_08'))
import fetch_author_web_identity as previous


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    previous.client.base.own_priority()
    previous.client.resource_guard()
    identity = json.loads((HERE/'author_attempt01/visible_identity.json').read_text(encoding='utf-8'))
    oid = identity['current_commit']
    assert oid == '224fc36c38d3fec46a907a74c4bc0e090998ad89'
    names = [r['path'] for r in identity['root_tree_items']
        if r['contentType']=='file' and r['path'].endswith('.py')]
    assert set(names) == {'data_loader.py', 'experts.py', 'moe_model.py', 'train_moediffer.py', 'vqvae.py'}
    OUT.mkdir(exist_ok=False)
    previous.fetcher.OUT = OUT
    rows = []
    for name in names:
        previous.client.resource_guard()
        row = previous.fetcher.get(name[:-3],
            'https://raw.githubusercontent.com/ZWang78/MoEDiff-SR/'+oid+'/'+name, 'source.txt')
        rows.append(row)
        assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file()) < 6_000_000
    receipt = dict(created_utc=datetime.now(timezone.utc).isoformat(),
        complete=all(r['complete'] for r in rows), errors=[e for r in rows for e in r['errors']],
        pinned_commit=oid, records=rows, actual_source_files_read=[],
        author_code_executed=False, medical_arrays_loaded=0, neural_forwards=0, GPU_forwards=0,
        source_bindings=[previous.client.base.entry(p) for p in [Path(__file__), HERE/'PROTOCOL.md',
            HERE/'author_attempt01/visible_identity.json', HERE/'author_attempt01/README.source.txt']],
        resource_snapshot=previous.client.resource_guard())
    previous.client.base.new(OUT/'receipt.json', receipt)
    print(json.dumps(receipt, ensure_ascii=False), flush=True)
    return int(not receipt['complete'])


if __name__ == '__main__':
    raise SystemExit(main())
