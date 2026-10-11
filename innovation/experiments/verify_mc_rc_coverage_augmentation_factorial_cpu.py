"""Authenticate four arms, all draw hashes, independent native metrics and 12 planes.

No training. Geometry reference is separate; checkpoint replay uses the same
architecture and therefore is implementation verification, not generalization.
"""
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
for key in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
    os.environ[key] = '1'
import copy
import hashlib
import json
import sys
import traceback
from datetime import datetime, timezone
from vs_seg_task_cpu_support import resource_gate
from mc_rc_global_local_task_cpu_support import (
    ROOT, SEED, GlobalLocalUNet, weight_hash, read, sha, array_sha,
    load_authenticated_observed, sparse_image, physical_shape, resize_image, np, torch)
from mc_rc_task_metrics_cpu import independent_label, independent_counts, independent_surface
from verify_mc_rc_global_local_task_validation_cpu import replay_plane

OUT = ROOT / 'experiments/mc_rc_coverage_augmentation_factorial_cpu'
ARMS = ('legacy_aug', 'legacy_none', 'coverage_aug', 'coverage_none')


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    resource_gate()
    source = OUT / 'attempt_01.json'
    r = read(source)
    assert r['complete'] and not r['errors'], 'Production still live or failed; do not verify/restart it.'
    path = OUT / 'independent_all_arms_metrics_draws_checkpoint_attempt_01.json'
    assert not path.exists(), 'Preserve completed/failed verifier attempts.'
    names = ('mc_rc_global_local_task_cpu_support.py', 'mc_rc_task_metrics_cpu.py',
             'verify_mc_rc_global_local_task_validation_cpu.py',
             'mc_rc_global_local_geometry_reference_cpu.py')
    q = dict(created_utc=datetime.now(timezone.utc).isoformat(), complete=False, errors=[],
             script_sha256=sha(__file__), result_file=source.relative_to(ROOT).as_posix(),
             result_sha256=sha(source), code_bindings=[dict(path='experiments/' + s,
             sha256=sha(ROOT / 'experiments' / s)) for s in names], arms=[],
             four_arm_training_draw_sha_checks=0, checkpoint_replayed_planes=0,
             training_updates=0, same_architecture_replay=True,
             second_independently_trained_generalization_model=False,
             native_hidden_MR_pixels_decoded=False, validation_patients_opened=False,
             confirmation_patients_opened=False, scientific_confirmation_patients=0,
             publication_claim_confirmed=False)
    write(path, q)
    try:
        assert tuple(a['name'] for a in r['arms']) == ARMS
        assert r['new_training_updates_completed'] == r['new_training_updates_planned'] == 12000
        assert r['training_patient_ids'] == ['VS-MC-RC-012']
        assert r['training_series_uids'] == [r['case_binding']['uid']]
        assert r['seed'] == SEED and r['updates_per_arm'] == 4000 and r['model_parameters'] == 981602
        assert r['device'] == 'cpu' and not r['gpu_initialized'] and not r['pretrained_weights_loaded']
        assert not r['validation_patients_opened'] and not r['confirmation_patients_opened']
        for binding in r['source_bindings'] + r['code_bindings']:
            assert sha(ROOT / binding['path']) == binding['sha256']
        assert sha(ROOT / r['protocol_file']) == r['protocol_sha256']
        assert sha(ROOT / 'experiments/run_mc_rc_coverage_augmentation_factorial_cpu.py') == r['script_sha256']
        d = read(ROOT / r['source_bindings'][0]['path'])
        dv = read(ROOT / r['source_bindings'][1]['path'])
        old = read(ROOT / r['source_bindings'][2]['path'])
        assert d['complete'] and dv['complete'] and not d['errors'] and not dv['errors']
        assert dv['result_sha256'] == r['source_bindings'][0]['sha256']
        assert dv['all_arm_real_input_sha_checks'] == dv['full_patch_geometry_checks'] == 16000
        assert dv['legacy_original_sampler_matches'] == 4000 and dv['legacy_baseline_exact_reuse_verified']
        for binding in d['source_bindings']:
            assert sha(ROOT / binding['path']) == binding['sha256']
        assert sha(ROOT / d['protocol_file']) == d['protocol_sha256']
        assert sha(ROOT / 'experiments/prepare_mc_rc_coverage_augmentation_draw_cpu.py') == d['script_sha256']
        assert sha(ROOT / 'experiments/mc_rc_coverage_augmentation_draw_cpu_support.py') == d['draw_support_sha256']
        assert len(d['rows']) == 4000 and tuple(d['arms']) == ARMS
        for binding in old['source_bindings'] + old['code_bindings']:
            assert sha(ROOT / binding['path']) == binding['sha256']
        assert sha(ROOT / old['protocol_file']) == old['protocol_sha256']
        assert sha(ROOT / 'experiments/run_mc_rc_global_local_single_case_loss_cpu.py') == old['script_sha256']
        case = r['case_binding']
        assert case == d['case_binding'] == old['case_binding'] and case['patient'] == 'VS-MC-RC-012'
        row = next(e for e in read(ROOT / 'experiments/mc_rc_development_training_input_cpu/attempt_01.json')['series']
                   if e['uid'] == case['uid'])
        obs = load_authenticated_observed(case, row)
        native, stats = sparse_image(obs, 'raw_pchip', row)
        label = independent_label(case)
        shape, spacing = physical_shape(case)
        image = resize_image(native, shape)
        assert image.shape[0] == label.shape[2] == 72
        b = r['input_binding']
        assert array_sha(native) == b['native_input_sha256'] == d['input_binding']['native_input_sha256']
        assert array_sha(image) == b['physical_input_sha256'] == d['input_binding']['physical_input_sha256']
        assert array_sha(label) == b['native_label_sha256'] == d['input_binding']['native_label_sha256']
        assert b['observed_statistics'] == stats
        inherited = copy.deepcopy(r['arms'][0])
        assert inherited.pop('name') == 'legacy_aug'
        for key, value in dict(reused_existing_arm=True, inherited_old_training_updates=4000,
            new_training_updates=0, new_global_forward_calls=0, new_local_forward_calls=0,
            origin_source_file=r['source_bindings'][2]['path'],
            origin_source_sha256=r['source_bindings'][2]['sha256']).items():
            assert inherited.pop(key) == value
        expected = copy.deepcopy(old['arms'][0])
        assert expected.pop('name') == 'bce_batch_dice' and inherited == expected
        for arm in r['arms']:
            resource_gate()
            assert arm['complete'] and arm['updates_completed'] == 4000 and len(arm['draw_sha256']) == 4000
            for step, record in enumerate(d['rows']):
                assert record['step'] == step and arm['draw_sha256'][step] == record['example_sha256_by_arm'][arm['name']]
                q['four_arm_training_draw_sha_checks'] += 1
            torch.manual_seed(SEED)
            model = GlobalLocalUNet()
            assert sum(p.numel() for p in model.parameters()) == 981602
            assert weight_hash(model) == arm['initial_weights_sha256'] == old['arms'][0]['initial_weights_sha256']
            cp = ROOT / arm['checkpoint_file']
            assert sha(cp) == arm['checkpoint_sha256']
            checkpoint = torch.load(cp, map_location='cpu', weights_only=True)
            assert checkpoint['updates_completed'] == 4000
            assert checkpoint['training_patient_ids'] == r['training_patient_ids']
            assert checkpoint['training_series_uids'] == r['training_series_uids']
            for key in ('initial_weights_sha256', 'final_weights_sha256'):
                assert checkpoint[key] == arm[key]
            if arm['name'] == 'legacy_aug':
                assert checkpoint['arm'] == 'bce_batch_dice'
                assert checkpoint['draw_stream_sha256'] == arm['draw_stream_sha256']
                stream = hashlib.sha256()
                for value in arm['draw_sha256']:
                    stream.update(value.encode())
                assert stream.hexdigest() == arm['draw_stream_sha256']
                assert arm['new_training_updates'] == arm['new_global_forward_calls'] == arm['new_local_forward_calls'] == 0
            else:
                assert checkpoint['arm'] == arm['name'] and checkpoint['seed'] == SEED
                assert checkpoint['protocol_sha256'] == r['protocol_sha256']
                assert checkpoint['draw_file_sha256'] == r['source_bindings'][0]['sha256']
                assert arm['new_training_updates'] == 4000 and not arm['reused_existing_arm']
                assert [h['update'] for h in arm['training_history']] == list(range(100, 4001, 100))
                assert arm['first10_updates_seconds_per_update'] <= 2
                assert arm['new_global_forward_calls'] == 4000 + 72
                assert arm['new_local_forward_calls'] == 4000 + 72 * 4
            model.load_state_dict(checkpoint['state_dict'], strict=True)
            model.eval()
            assert weight_hash(model) == arm['final_weights_sha256']
            e = arm['evaluation']
            assert e['patient'] == case['patient'] and e['uid'] == case['uid']
            pp = ROOT / e['prediction_file']
            assert sha(pp) == e['prediction_file_sha256']
            with np.load(pp, allow_pickle=False) as data:
                assert data.files == ['prediction_rcz']
                pred = data['prediction_rcz'].copy()
            assert pred.shape == label.shape == tuple(case['native_shape']) and pred.dtype == bool
            assert array_sha(pred) == e['prediction_array_sha256']
            n = pred.shape[2]
            last = ((n - 1) // 4) * 4
            domains = dict(full=list(range(n)), anchors=list(range(0, n, 4)),
                           missing=[z for z in range(last) if z % 4], tail=list(range(last + 1, n)))
            assert sorted(domains['anchors'] + domains['missing'] + domains['tail']) == domains['full']
            counts = {}
            for domain, zs in domains.items():
                value = independent_counts(pred[:, :, zs], label[:, :, zs])
                assert all(e['metrics'][domain][k] == v for k, v in value.items())
                if domain != 'full':
                    assert e['metrics'][domain]['planes'] == len(zs)
                counts[domain] = value
            surface = independent_surface(pred, label, case['affine_rcz_ras'])
            for key, value in surface.items():
                if value is None:
                    assert e['metrics']['full_surface'][key] is None
                else:
                    assert abs(e['metrics']['full_surface'][key] - value) < .0001
            volume = abs(float(np.linalg.det(np.asarray(case['affine_rcz_ras'])[:3, :3])))
            assert abs(e['metrics']['voxel_volume_mm3'] - volume) < 1e-12
            checks = dict(full_dice=counts['full']['dice'] >= .9, missing_dice=counts['missing']['dice'] >= .9,
                          full_recall=counts['full']['recall'] >= .9,
                          full_absRVE=counts['full']['absolute_relative_volume_error'] <= .1)
            assert checks == e['fit_gate_checks'] and all(checks.values()) == e['fit_gate_passed']
            coverage = e['coverage']
            assert coverage['physical_input_shape'] == list(image.shape) and coverage['planes'] == list(range(n))
            assert coverage['tiles_per_plane'] == 16
            planes = []
            for z in (0, n // 2, n - 1):
                direct, cov, axes = replay_plane(model, image, z, spacing, case['native_shape'])
                mismatches = int(np.count_nonzero(direct != pred[:, :, z]))
                q['last_replay_check'] = dict(arm=arm['name'], z=z, prediction_voxel_mismatches=mismatches)
                write(path, q)
                assert mismatches == 0 and array_sha(cov) == coverage['coverage_sha256']
                assert axes == [coverage['row_starts'], coverage['col_starts']]
                assert int(cov.min()) == coverage['coverage_min'] and int(cov.max()) == coverage['coverage_max']
                planes.append(z)
                q['checkpoint_replayed_planes'] += 1
            q['arms'].append(dict(name=arm['name'], independent_counts=counts,
                independent_surface=surface, fit_gate_checks_verified=checks,
                fit_gate_passed_verified=e['fit_gate_passed'], checkpoint_replayed_planes=planes,
                global_forward_calls=model.global_calls, local_forward_calls=model.local_calls))
            write(path, q)
            print(json.dumps(dict(arm=arm['name'], native_metrics_verified=True, complete_planes_replayed=3)), flush=True)
            del model, checkpoint, pred
        assert r['global_forward_calls'] == sum(a['new_global_forward_calls'] for a in r['arms']) == 12216
        assert r['local_forward_calls'] == sum(a['new_local_forward_calls'] for a in r['arms']) == 12864
        assert sha(source) == q['result_sha256'], 'Result changed during verification.'
        q['global_forward_calls'] = sum(a['global_forward_calls'] for a in q['arms'])
        q['local_forward_calls'] = sum(a['local_forward_calls'] for a in q['arms'])
        q['gpu_initialized'] = torch.cuda.is_initialized()
        assert not q['gpu_initialized']
        q['complete'] = len(q['arms']) == 4 and q['four_arm_training_draw_sha_checks'] == 16000 and q['checkpoint_replayed_planes'] == 12
    except Exception as error:
        q['errors'].append(type(error).__name__ + ': ' + str(error))
        q['traceback'] = traceback.format_exc()
    q['finished_utc'] = datetime.now(timezone.utc).isoformat()
    write(path, q)
    print(json.dumps({k: q.get(k) for k in ('complete', 'errors', 'four_arm_training_draw_sha_checks',
        'checkpoint_replayed_planes', 'global_forward_calls', 'local_forward_calls', 'gpu_initialized')}), flush=True)
    return int(not q['complete'])


if __name__ == '__main__':
    raise SystemExit(main())
