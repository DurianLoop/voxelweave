"""Full public MSLesSeg table/directory join; no pixels or model imports."""
from __future__ import annotations
import ast
import csv
import hashlib
import json
import math
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'literature/source_cache/mslesseg_public_zip_metadata_2026-10-02'
OUT = ROOT / 'experiments/mslesseg_scan_metadata_gate'
PLAN = ROOT / 'MSLESSEG_SCAN_METADATA_AND_HEADER_PLAN_2026-10-02.md'

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def key(row):
    return (row.get('Patient', '').strip(), row.get('Timepoint', '').strip())

def numeric(s):
    try:
        n = float(s)
        return n if math.isfinite(n) and n > 0 else None
    except (ValueError, TypeError):
        return None

def file_key(path, registered):
    name = Path(path).name
    m = re.fullmatch(r'(P\d+)_(T\d+)_(T1|T2|FLAIR|MASK)\.nii\.gz', name)
    if m:
        return (m[1], m[2]), m[3], 'explicit_timepoint'
    m = re.fullmatch(r'(P\d+)_(T1|T2|FLAIR|MASK)\.nii\.gz', name)
    if registered and m:
        return (m[1], 'T1'), m[2], 'test_T1_inferred_from_filename'
    raise ValueError('Unrecognized public member naming: ' + path)

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True, exist_ok=True)
    attempt = len(list(OUT.glob('attempt_*.json'))) + 1
    source = json.loads((SOURCE/'attempt_01.json').read_text(encoding='utf-8'))
    tables, table_stats, anomalies = {}, {}, []
    for name, index in [('clinical', 0), ('FLAIR', 1), ('T1', 2), ('T2', 3)]:
        p = SOURCE / f'registered_metadata_{index:02d}_attempt_01.csv'
        with p.open(encoding='utf-8-sig', newline='') as f:
            rows = list(csv.DictReader(f, delimiter=';'))
        by_key = {}
        for row_number, row in enumerate(rows, 2):
            k = key(row)
            if not re.fullmatch(r'P\d+', k[0]) or not re.fullmatch(r'T\d+', k[1]):
                anomalies.append({'table': name, 'line': row_number, 'kind': 'invalid_key', 'row': row})
                continue
            if k in by_key:
                anomalies.append({'table': name, 'line': row_number, 'kind': 'duplicate_key', 'key': list(k)})
            by_key[k] = row
        tables[name] = by_key
        thick = [numeric(r.get('SliceThickness[mm]')) for r in by_key.values()]
        table_stats[name] = {'file': p.name, 'sha256': sha(p), 'rows': len(rows),
                            'valid_unique_scan_keys': len(by_key), 'patients': len({k[0] for k in by_key}),
                            'thickness_raw_counts': dict(Counter(r.get('SliceThickness[mm]', 'not_a_field') for r in by_key.values())),
                            'numeric_thickness_count': sum(x is not None for x in thick),
                            'unknown_thickness_count': sum(x is None for x in thick),
                            'numeric_thickness_le_1_5mm': sum(x is not None and x <= 1.5 for x in thick)}
    inventory, split = {}, {}
    for archive in source['records']:
        mode = archive['key']
        inventory[mode] = {}
        for member in archive['members']:
            if not member['path'].endswith('.nii.gz'):
                continue
            k, modality, assumption = file_key(member['path'], mode == 'registered')
            maps = inventory[mode].setdefault(modality, {})
            if k in maps:
                raise ValueError(f'Duplicate member key: {mode} {modality} {k}')
            maps[k] = {'path': member['path'], 'timepoint_status': assumption}
            if mode == 'registered':
                split.setdefault(member['path'].split('/')[1], set()).add(k)
    reg, raw, t2 = inventory['registered']['T2'], inventory['raw']['T2'], tables['T2']
    all_keys = sorted(set(reg) | set(raw) | set(t2), key=lambda k: (int(k[0][1:]), int(k[1][1:])))
    scans = []
    for k in all_keys:
        row = t2.get(k, {})
        spacing = None
        try:
            parsed = ast.literal_eval(row.get('PixelSpacing', ''))
            if len(parsed) == 2 and all(numeric(x) is not None for x in parsed):
                spacing = [float(x) for x in parsed]
        except (ValueError, SyntaxError, TypeError):
            pass
        thickness = numeric(row.get('SliceThickness[mm]'))
        scans.append({'patient': k[0], 'timepoint': k[1], 'registered': reg.get(k), 'raw': raw.get(k),
                      'csv_record': row or None, 'reported_thickness_mm': thickness,
                      'reported_inplane_spacing_mm': spacing,
                      'csv_thin_candidate': bool(thickness is not None and thickness <= 1.5 and spacing and max(spacing) <= 1.5),
                      'native_thin_acquisition_certified': False, 'raw_label_mapping_certified': False})
    differences = {'raw_T2_without_registered': [list(k) for k in sorted(set(raw)-set(reg))],
                   'registered_T2_without_raw': [list(k) for k in sorted(set(reg)-set(raw))],
                   'registered_T2_without_csv': [list(k) for k in sorted(set(reg)-set(t2))],
                   'csv_T2_without_registered': [list(k) for k in sorted(set(t2)-set(reg))]}
    counts = {mode: {mod: {'scans': len(rows), 'patients': len({k[0] for k in rows})} for mod, rows in data.items()}
              for mode, data in inventory.items()}
    result = {'attempt': attempt, 'created_utc': datetime.now(timezone.utc).isoformat(),
              'script_sha256': sha(__file__), 'plan_sha256': sha(PLAN), 'inventory_source_sha256': sha(SOURCE/'attempt_01.json'),
              'scope': 'public metadata only; key alignment is not spatial/native sampling certification',
              'tables': table_stats, 'directory_counts': counts,
              'registered_splits': {s: {'scans': len(keys), 'patients': len({k[0] for k in keys}),
                                        'patient_ids': sorted({k[0] for k in keys}, key=lambda p: int(p[1:]))} for s, keys in split.items()},
              'differences': differences, 'anomalies': anomalies, 'scans': scans,
              'csv_thin_T2_candidates': sum(r['csv_thin_candidate'] for r in scans),
              'certified_native_thin_T2_scans': 0, 'patient_pixels_decoded': False}
    (OUT/f'attempt_{attempt:02d}.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k not in ('scans',)}, ensure_ascii=False, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
