"""Compress only the preselected immutable offline texts; preserve every logical byte."""
import json
import subprocess
import sys
import time
from pathlib import Path

from inventory_frozen_text_storage import ROOT, HERE, EXTENSIONS, sha, entry, dump, physical
from mc_rc_reference_resources_2026_10_07 import resource_guard

INVENTORY = HERE / 'inventory_attempt01/receipt.json'
INVENTORY_SHA = 'b446e2371f74ca123b9ac5ac87a0f1397715bcf0b5c28a7acf665425c1caa028'
RESERVED_OTHER_OUTPUTS = 2_000_000 + 3_000_000 + 2_800_000


def guard(started):
    resources = resource_guard()
    assert time.perf_counter() - started < 300, 'Recovery wall limit'
    assert resources['workspace_free_bytes'] - RESERVED_OTHER_OUTPUTS - 2_000_000 >= 8_000_000_000
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file()) < 2_000_000
    return resources


def checked_source(binding):
    path = (ROOT / binding['path']).resolve()
    assert path.is_relative_to(ROOT) and path.suffix.lower() in EXTENSIONS
    assert not path.is_relative_to(ROOT / 'tools')
    assert not path.is_relative_to(ROOT / 'full_real_intensity_v2_2026_10_09/full_real_pipeline_attempt01')
    assert path.is_file() and path.stat().st_size == binding['bytes']
    assert sha(path) == binding['sha256'], 'Frozen source content mismatch'
    return path


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    started = time.perf_counter()
    before = guard(started)
    assert sha(INVENTORY) == INVENTORY_SHA
    inventory = json.loads(INVENTORY.read_text(encoding='utf-8'))
    assert inventory['complete'] and not inventory['errors']
    assert inventory['known_frozen_files'] == 6923 and not inventory['compression_executed']
    selected = inventory['selected']
    assert len(selected) == 40 and sum(row['source_binding']['bytes'] for row in selected) == 62_855_339
    assert len({row['source_binding']['path'] for row in selected}) == 40
    planned = []
    for row in selected:
        guard(started)
        path = checked_source(row['source_binding'])
        state = physical(path)
        assert not state['compressed'], 'Already compressed since inventory; stop for new plan'
        assert not state['attributes'] & (0x1 | 0x200 | 0x4000 | 0x400), 'Unsupported file attributes'
        planned.append(dict(source_binding=row['source_binding'],absolute_path=str(path),storage_before=state))
    out = HERE / 'compression_attempt01'
    out.mkdir(exist_ok=False)
    planpath = out / 'planned_targets.json'
    dump(planpath, dict(frozen_before_execution=True,inventory=entry(INVENTORY),targets=planned,
                       resources_before=before,compact_arguments=['/C','/I','/Q'],timeout_seconds=30))
    result = dict(complete=False,errors=[],planned_files=40,files=[],logical_bytes=62_855_339,
                  plan=entry(planpath),resources_before=before,compression_executed=True,
                  MRI_model_or_live_files_selected=False,other_PIDs_enumerated=False,
                  other_PIDs_modified=False,source_logical_bytes_or_paths_modified=False,
                  publication_claim_confirmed=False,goal_status='active')
    try:
        for target in planned:
            guard(started)
            path = checked_source(target['source_binding'])
            assert physical(path) == target['storage_before'], 'Storage metadata changed since plan'
            call = subprocess.run(['compact.exe','/C','/I','/Q',str(path)],
                                  capture_output=True,text=True,errors='replace',timeout=30)
            unchanged = path.stat().st_size == target['source_binding']['bytes'] and sha(path) == target['source_binding']['sha256']
            after = physical(path)
            row = dict(source_binding=target['source_binding'],compact_exit=call.returncode,
                       stdout=call.stdout,stderr=call.stderr,storage_before=target['storage_before'],
                       storage_after=after,logical_bytes_and_SHA_unchanged=unchanged,
                       API_physical_bytes_saved=target['storage_before']['physical_bytes']-after['physical_bytes'],
                       resources_after=resource_guard())
            result['files'].append(row)
            assert unchanged, 'Frozen logical bytes changed; stop immediately'
            assert call.returncode == 0 and after['compressed'], 'Compression failed; stop immediately'
            if len(result['files']) % 5 == 0:
                print(json.dumps(dict(processed=len(result['files']),planned=40,
                                      API_saved_bytes=sum(x['API_physical_bytes_saved'] for x in result['files']))),flush=True)
        result['complete'] = True
    except Exception as exc:
        result['errors'].append(dict(type=type(exc).__name__,message=str(exc)))
    result.update(files_processed=len(result['files']),
                  all40_frozen_logical_bytes_and_hashes_verified=result['complete'],
                  API_physical_bytes_saved=sum(x['API_physical_bytes_saved'] for x in result['files']),
                  workspace_free_bytes_after=__import__('shutil').disk_usage(ROOT).free,
                  elapsed_seconds=time.perf_counter()-started,
                  source_bindings=[entry(Path(__file__)),entry(HERE/'PROTOCOL.md'),entry(INVENTORY)])
    dump(out / 'receipt.json',result)
    print(json.dumps({key:value for key,value in result.items() if key not in ['files','source_bindings']},ensure_ascii=False),flush=True)
    return int(not result['complete'])


if __name__ == '__main__':
    raise SystemExit(main())
