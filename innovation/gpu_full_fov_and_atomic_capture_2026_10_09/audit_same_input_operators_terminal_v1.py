"""Independent stdlib audit of completed same-input probes; no model/GPU execution."""
import ctypes, gzip, hashlib, itertools, json, math, shutil, time, traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

def bind(item):
    path = ROOT / item['path']
    assert path.is_relative_to(ROOT) and path.is_file()
    assert path.stat().st_size == item['bytes'] and sha(path) == item['sha256'], item['path']
    return path

def main():
    started = time.perf_counter()
    kernel = ctypes.windll.kernel32
    kernel.GetCurrentProcess.restype = ctypes.c_void_p
    assert kernel.SetPriorityClass(ctypes.c_void_p(kernel.GetCurrentProcess()), 0x4000)
    assert shutil.disk_usage(ROOT).free >= 8_000_000_000
    out = HERE / 'same_input_terminal_audit_attempt01'
    out.mkdir(exist_ok=False)
    r = dict(complete=False, errors=[], CUDA_initialized=False, MRI_arrays_loaded=0,
             GT_arrays_loaded=0, model_arrays_loaded=0, training_updates=0,
             full38_FOV_qualified=False, medical_effect_scored=False,
             publication_claim_confirmed=False, goal_status='active')
    try:
        terminal_path = HERE / 'ACTUAL_SAME_INPUT_OPERATORS_TERMINAL_TOOL.json'
        terminal = read(terminal_path)
        assert terminal['exit_code'] == 0 and 'session_id' not in terminal
        assert terminal['observed_unified_exec_session'] == 6897
        last = json.loads(terminal['output'].strip().splitlines()[-1])
        attempt = HERE / 'same_input_operators_attempt01'
        receipt = read(attempt / 'receipt.json')
        cfg = read(attempt / 'frozen_config.json')
        assert last['complete'] and last['status'] == 'completed' and not last['errors']
        assert receipt['complete'] and receipt['status'] == 'completed' and not receipt['errors']
        assert last['batches_completed'] == receipt['batches_completed'] == 96
        assert last['elapsed_seconds'] == receipt['elapsed_seconds']
        assert sha(attempt / 'frozen_config.json') == receipt['frozen_config_sha256']
        for item in cfg['source_bindings']:
            bind(item)
        assert receipt['source_bindings'] == cfg['source_bindings']
        primary = {f'encoders.{i}.layers.{j}' for i in range(4) for j in range(6)}
        primary |= {f'decoders.{i}.layers.{j}' for i in range(3) for j in range(6)}
        primary |= {f'{kind}.{i}' for kind in ('heads','ups') for i in range(3)}
        primary.add('probability')
        auxiliary = {f'auxiliary.max_pool.{i}' for i in range(1,4)}
        assert len(primary) == 49 and len(auxiliary) == 3
        assert cfg['expected_batches'] == 96 and cfg['expected_unique_tiles'] == 192
        assert cfg['batch_size'] == cfg['repeat_per_operator_device'] == 2
        assert cfg['expected_primary_fields'] == 49 and cfg['expected_auxiliary_fields'] == 3
        locations = [list(v) for v in itertools.product(*cfg['axis_starts'])]
        assert len(locations) == len({tuple(v) for v in locations}) == 192
        old_path = HERE / 'layerwise_all_tiles_attempt01/batches.jsonl.gz'
        with gzip.open(old_path, 'rt', encoding='utf-8') as f:
            old_rows = [json.loads(line) for line in f]
        journal = bind(receipt['journal'])
        maxima = {}; count = 0; all_starts = []; evaluations = 0
        with gzip.open(journal, 'rt', encoding='utf-8') as f:
            for batch, line in enumerate(f):
                row = json.loads(line); count += 1
                assert row['batch'] == batch and row['tile_starts'] == locations[batch*2:batch*2+2]
                assert row['tile_starts'] == old_rows[batch]['tile_starts']
                all_starts.extend(row['tile_starts'])
                assert row['primary_fields'] == 49 and row['auxiliary_fields'] == 3
                assert row['CPU_batch_original_probability_sha_reproduced']
                assert row['CPU_batch_probability_sha256'] == old_rows[batch]['CPU_batch_probability_sha256']
                checks = row['operator_checks']
                assert len(checks) == 52 and {v['name'] for v in checks} == primary | auxiliary
                for check in checks:
                    name = check['name']; shape = check['shape']
                    assert len(shape) == 5 and shape[0] == 2 and math.prod(shape) == check['elements']
                    assert all(isinstance(n, int) and n > 0 for n in shape)
                    assert check['role'] == ('auxiliary_pool' if name in auxiliary else 'primary_leaf_or_probability')
                    for key in ('CPU_operator_repeat_bitwise_equal','GPU_operator_repeat_bitwise_equal','GPU_input_transfer_bitwise_equal'):
                        assert check[key] is True
                    for key in ('CPU_input_sha256','CPU_output_sha256','GPU_output_sha256'):
                        assert len(check[key]) == 64 and all(c in '0123456789abcdef' for c in check[key])
                    error = check['max_absolute_error']; mean = check['mean_absolute_error']
                    assert math.isfinite(error) and math.isfinite(mean) and 0 <= mean <= error
                    assert len(check['maximum_error_index']) == 5
                    assert all(0 <= i < n for i,n in zip(check['maximum_error_index'],shape))
                    assert abs(abs(check['maximum_error_CPU_value']-check['maximum_error_GPU_value'])-error) <= 1e-12
                    if error == 0:
                        assert check['CPU_output_sha256'] == check['GPU_output_sha256']
                    if name not in maxima or error > maxima[name]['max_absolute_error']:
                        maxima[name] = dict(check,batch=batch,tile_starts=row['tile_starts'])
                    evaluations += 2
                assert next(v for v in checks if v['name']=='probability')['CPU_output_sha256'] == row['CPU_batch_probability_sha256']
        assert count == 96 and all_starts == locations and len({tuple(v) for v in all_starts}) == 192
        assert maxima == receipt['layer_maxima'] and evaluations == 9984
        assert receipt['primary_fields_completed'] == 4704 and receipt['auxiliary_fields_completed'] == 288
        assert receipt['actual_CPU_operator_evaluations'] == receipt['actual_GPU_operator_evaluations'] == evaluations
        old_full = read(HERE / 'full_fov_attempt01/receipt.json')['series'][-1]
        assert receipt['CPU_original_fullFOV_probability_sha256'] == old_full['CPU_probability_sha256']
        assert receipt['CPU_original_all96_batch_probability_hashes_reproduced'] and receipt['CPU_original_fullFOV_hash_reproduced']
        assert receipt['all52_same_device_operator_repeats_bitwise_equal']
        assert receipt['coordinate_error'] <= 3e-12 and receipt['coordinate_binary_disagreements'] == 0
        assert not receipt['new_GPU_whole_model_FOV_run'] and not receipt['full38_FOV_qualified']
        assert receipt['training_updates'] == receipt['GT_arrays_loaded'] == 0
        assert receipt['resources_after']['GPU_peak_reserved_bytes'] <= 2_500_000_000
        assert receipt['resources_after']['GPU_free_bytes'] >= 4_000_000_000
        assert receipt['resources_after']['workspace_free_bytes'] >= 8_000_000_000
        assert sum(receipt['cost_seconds'].values()) <= receipt['elapsed_seconds']
        r.update(complete=True,all96_batches192_unique_tiles4704_primary288_auxiliary_verified=True,
                 all52_maxima_recomputed=True,actual_operator_evaluations_per_device=evaluations,
                 source_bindings_verified=len(cfg['source_bindings']),all_batch_CPU_hashes_matched=True,
                 CPU_fullFOV_hash_matched=True,coordinate_gate_passed=True,
                 layer_maximum_errors={k:v['max_absolute_error'] for k,v in maxima.items()},
                 record_level_evidence_only=True,new_GPU_whole_model_FOV_run=False)
        r['source_bindings'] = [dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in
                               (Path(__file__),terminal_path,attempt/'receipt.json',attempt/'frozen_config.json',journal,old_path)]
    except Exception as e:
        r['errors'].append(type(e).__name__+': '+str(e)); r['traceback']=traceback.format_exc()
    r['elapsed_seconds']=time.perf_counter()-started
    (out/'receipt.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in r.items() if k not in ('source_bindings','layer_maximum_errors')}),flush=True)
    return int(not r['complete'])

if __name__ == '__main__':
    raise SystemExit(main())
