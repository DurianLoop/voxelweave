"""Read-only checks for the 2026-10-23 documentation/evidence handoff.

This does not execute training, inference, clinical evaluation, or pickle loads.
Run from any directory: python processing/verify_research_handoff.py
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / 'docx/experiment'
EVIDENCE = DOC / 'handoff_evidence_20261023'
MASTER_SHA256 = '9a4c78ab4e0bfff11152684ea1ba5a7d206f8835e05e2c61d384497a0c485dfe'
MASTER_LF_SHA256 = 'b149b5de148c4ebb04fdc52bb4971f235d04b4ddfe3458d623940f1ba1752059'


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-local-checkpoints', action='store_true',
                        help='Also require local checkpoint files and verify their hashes; no model is loaded.')
    args = parser.parse_args()
    errors: list[str] = []
    docs = [ROOT / 'README.md', DOC / 'self_innovation_methods_and_results.md',
            DOC / 'self_model_baseline_tiers.md', DOC / 'research_handoff_20261023.md',
            *sorted(EVIDENCE.rglob('*.md'))]
    link_count = 0
    for path in docs:
        try:
            text = path.read_text(encoding='utf-8-sig')
        except (OSError, UnicodeError) as error:
            errors.append(f'{path}: {error}')
            continue
        if '\ufffd' in text or re.search(r'\?{4,}', text):
            errors.append(f'{path}: potential encoding damage')
        fence = False
        columns = None
        for number, line in enumerate(text.splitlines(), 1):
            if line.startswith('```'):
                fence = not fence
                columns = None
            if not fence and line.startswith('|') and line.endswith('|'):
                count = len(re.split(r'(?<!\\)\|', line)) - 2
                if columns is None:
                    columns = count
                elif count != columns:
                    errors.append(f'{path}:{number}: table columns {count} != {columns}')
            else:
                columns = None
        if fence:
            errors.append(f'{path}: unbalanced code fences')
        for target in re.findall(r'(?<!!)\[[^\]\n]+\]\(([^\n)]+)\)', text):
            target = target.strip('<>')
            if target.startswith(('https://', 'http://', '#', 'mailto:')):
                continue
            link_count += 1
            target = unquote(target.split('#', 1)[0])
            if not (path.parent / target).resolve().exists():
                errors.append(f'{path}: missing link {target}')

    copied = 0
    catalog = read_csv(EVIDENCE / 'source_availability.csv')
    for item in catalog:
        if item['status'] != 'copied aggregate evidence':
            continue
        path = ROOT / item['archived_path']
        if not path.is_file() or sha256(path) != item['sha256']:
            errors.append(f'Invalid evidence snapshot: {path}')
        elif path.stat().st_size != int(item['bytes']):
            errors.append(f'Invalid snapshot size: {path}')
        copied += 1
    master = DOC / 'experiment_master_table.md'
    master_lf_sha256 = hashlib.sha256(master.read_bytes().replace(b'\r\n', b'\n')).hexdigest()
    if master_lf_sha256 != MASTER_LF_SHA256:
        errors.append('Original experiment_master_table.md changed; review protocol/data version.')

    rows = read_csv(DOC / 'self_model_baseline_comparison.csv')
    if len(rows) != 79:
        errors.append(f'Expected 79 comparison rows, found {len(rows)}')
    self_fast = [row for row in rows if row['dataset'] == 'fastMRI-T2' and row['kind'] == 'self-developed']
    if len(self_fast) != 38:
        errors.append(f'Expected 38 completed historical fastMRI full profiles, found {len(self_fast)}')
    seen = set()
    for row in rows:
        key = (row['protocol'], row['dataset'], row['method'])
        if key in seen:
            errors.append(f'Duplicate comparison row: {key}')
        seen.add(key)
        if not all(math.isfinite(float(row[metric])) for metric in ['psnr','ssim','mae','mse','ncc']):
            errors.append(f'Non-finite metric: {key}')
        reference = next((r for r in rows if r['dataset'] == row['dataset']
                          and r['method'] == row['best_baseline']), None)
        if reference is None:
            errors.append(f'Missing reference: {key}')
        elif abs(float(row['delta_psnr_best_baseline']) -
                 (float(row['psnr']) - float(reference['psnr']))) > 1e-12:
            errors.append(f'Incorrect PSNR delta: {key}')
    g086 = next(row for row in self_fast if row['method'] == 'full_pastnet_g086_dual_restart60')
    if abs(float(g086['delta_psnr_best_baseline']) - .4367774689695) > 1e-10:
        errors.append('G086 historical PSNR delta failed')

    checkpoints = read_csv(EVIDENCE / 'checkpoint_inventory.csv')
    if args.check_local_checkpoints:
        for item in checkpoints:
            path = ROOT / item['repo_relative_path']
            if not path.is_file() or sha256(path) != item['sha256']:
                errors.append(f'Missing/changed local checkpoint: {path}')
    report = dict(status='PASS' if not errors else 'FAIL',
                  checked_documents=len(docs), local_links=link_count,
                  source_records=len(catalog), byte_identical_evidence_files=copied,
                  comparison_rows=len(rows), historical_fastmri_full=len(self_fast),
                  checkpoint_inventory_rows=len(checkpoints),
                  checked_local_checkpoints=args.check_local_checkpoints,
                  original_master_sha256=sha256(master), errors=errors)
    report['original_master_lf_sha256'] = master_lf_sha256
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
