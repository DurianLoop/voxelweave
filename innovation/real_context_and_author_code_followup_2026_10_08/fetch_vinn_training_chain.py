"""Fetch bounded public pinned training sources. Never import author files."""
import sys, time, json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / 'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import entry, dump, resource_guard, read, sha
from fetch_pinned_vinn_code import get

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    resource_guard()
    started = time.perf_counter()
    predecessor = HERE / 'vinn_code_attempt02/receipt.json'
    previous = read(predecessor)
    assert previous['complete'] and not previous['errors']
    commit = previous['pinned_commit']
    assert commit == '550e84596b7adbc01bd0f2e93f1a127b1cb2df99'
    out = HERE / 'vinn_training_chain_attempt01'
    out.mkdir(exist_ok=False)
    paths = ['FastSurferCNN/config/defaults.py', 'FastSurferCNN/train.py',
             'FastSurferCNN/data_loader/loader.py', 'FastSurferCNN/data_loader/dataset.py',
             'FastSurferCNN/config/FastSurferVINN_axial.yaml',
             'FastSurferCNN/config/FastSurferVINN_coronal.yaml',
             'FastSurferCNN/config/FastSurferVINN_sagittal.yaml']
    def fetch(rel):
        dest = out / rel.replace('/', '__')
        url = 'https://raw.githubusercontent.com/Deep-MI/FastSurfer/' + commit + '/' + rel
        r = dict(repo_path=rel, url=url, complete=False, errors=[], actually_read=False)
        try:
            get(url, dest)
            r.update(complete=True, source_binding=entry(dest),
                     lines=len(dest.read_text(encoding='utf-8').splitlines()))
        except Exception as exc:
            r['errors'].append(type(exc).__name__ + ': ' + str(exc))
        return r
    with ThreadPoolExecutor(max_workers=2) as pool:
        records = list(pool.map(fetch, paths))
    errors = [e for r in records for e in r['errors']]
    result = dict(complete=not errors, errors=errors, records=records, pinned_commit=commit,
                  elapsed_seconds=time.perf_counter()-started, author_sources_imported=False,
                  author_sources_executed=False, author_training_reproduced=False,
                  new_distinct_primary_maintexts_completed=0, medical_arrays_loaded=0,
                  new_patient_medical_effects=0, publication_claim_confirmed=False, goal_status='active',
                  source_bindings=[entry(p) for p in [Path(__file__), HERE/'AUTHOR_TRAINING_CONFIG_PROTOCOL.md', predecessor]])
    dump(out/'receipt.json', result)
    assert sum(p.stat().st_size for p in out.rglob('*') if p.is_file()) < 1_500_000
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file()) < 5_000_000
    assert time.perf_counter()-started < 180
    print(json.dumps(result), flush=True)
    return int(bool(errors))

if __name__ == '__main__':
    raise SystemExit(main())
