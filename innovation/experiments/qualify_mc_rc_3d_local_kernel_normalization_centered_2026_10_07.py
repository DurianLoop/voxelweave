"""Preserve Eq5 FP32 failures; qualify explicitly centered units with independent reference."""
import json, sys, time, traceback
from datetime import datetime, timezone
from mc_rc_3d_baseline_v2_2026_10_07 import ROOT, sha, resource_guard, torch, np
from mc_rc_3d_local_kernel_normalization_2026_10_07 import local_kernel_conv3d
from mc_rc_3d_local_kernel_normalization_centered_2026_10_07 import local_kernel_conv3d_centered
OUT = ROOT/'experiments/mc_rc_3d_local_kernel_normalization_centered_2026_10_07'


def explicit(x, w, b, stride=(1, 1, 1), padding=(1, 1, 1), eps=1e-5):
    kernel = w.shape[2:]
    padded = np.pad(x.astype(np.float64), ((0, 0), (0, 0), *((p, p) for p in padding)))
    shape = tuple((n+2*p-k)//s+1 for n, p, k, s in zip(x.shape[2:], padding, kernel, stride))
    out = np.empty((x.shape[0], w.shape[0], *shape), dtype=np.float64)
    for n in range(x.shape[0]):
        for index in np.ndindex(shape):
            slabs = tuple(slice(i*s, i*s+k) for i, s, k in zip(index, stride, kernel))
            box = padded[(n, slice(None), *slabs)]
            normalized = (box-box.mean())/np.sqrt(box.var()+eps)
            out[(n, slice(None), *index)] = np.einsum('izrc,oizrc->o', normalized, w.astype(np.float64))+b
    return out


def main():
    sys.stdout.reconfigure(encoding='utf-8'); OUT.mkdir(exist_ok=False)
    path = OUT/'attempt01.json'; started = time.perf_counter()
    source = ROOT/'experiments/mc_rc_3d_local_kernel_normalization_2026_10_07/attempt01.json'
    r = dict(created_utc=datetime.now(timezone.utc).isoformat(), complete=False, errors=[], cases=[],
        script_sha256=sha(__file__), original_result_file=source.relative_to(ROOT).as_posix(), original_result_sha256=sha(source),
        source_bindings=[dict(path=p, sha256=sha(ROOT/p)) for p in (
            'MC_RC_3D_LOCAL_NORMALIZATION_NUMERICAL_ADDENDUM_2026-10-07.md',
            'experiments/mc_rc_3d_local_kernel_normalization_2026_10_07.py',
            'experiments/mc_rc_3d_local_kernel_normalization_centered_2026_10_07.py')],
        actual_training_updates=0, actual_gpu_updates=0, mri_or_label_values_loaded=0,
        confirmation_patients_opened=False, publication_claim_confirmed=False,
        known_operator_not_novel=True, full_architecture_or_training_recipe_implemented=False, dropout_probability=0)
    def save(): path.write_text(json.dumps(r, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    save()
    try:
        resource_guard(); rng = np.random.default_rng(20261007)
        w = rng.normal(scale=.1, size=(4, 3, 3, 3, 3)); b = rng.normal(scale=.1, size=4)
        examples = [('random', rng.normal(size=(2, 3, 7, 8, 9))), ('constant_two', np.full((1, 3, 7, 8, 9), 2.)),
                    ('zero', np.zeros((1, 3, 7, 8, 9))), ('offset_1000', rng.normal(size=(1, 3, 7, 8, 9))+1000),
                    ('offset_1e6', rng.normal(size=(1, 3, 7, 8, 9))+1e6),
                    ('near_constant_2', 2+rng.normal(scale=1e-4, size=(1, 3, 7, 8, 9)))]
        for dtype in (np.float64, np.float32):
            for name, raw in examples:
                x, weights, bias = [np.asarray(v, dtype=dtype) for v in (raw, w, b)]
                reference = explicit(x, weights, bias)
                with torch.inference_mode():
                    old = local_kernel_conv3d(torch.from_numpy(x), torch.from_numpy(weights), torch.from_numpy(bias)).numpy()
                    new = local_kernel_conv3d_centered(torch.from_numpy(x), torch.from_numpy(weights), torch.from_numpy(bias)).numpy()
                tolerance = 3e-6 if dtype == np.float32 else 1e-7
                row = dict(case=name, dtype=np.dtype(dtype).name, output_dtype=str(new.dtype), strict_tolerance=tolerance,
                    original_moment_max_error=float(np.max(np.abs(old-reference))),
                    centered_max_error=float(np.max(np.abs(new-reference))), all_outputs_finite=bool(np.isfinite(new).all()))
                row['strict_gate_passed'] = row['all_outputs_finite'] and row['centered_max_error'] <= tolerance
                r['cases'].append(row); save()
            for stride, padding in [((2, 2, 2), (1, 1, 1)), ((1, 1, 1), (0, 0, 0))]:
                x, weights, bias = [np.asarray(v, dtype=dtype) for v in (examples[0][1], w, b)]
                reference = explicit(x, weights, bias, stride, padding)
                with torch.inference_mode():
                    new = local_kernel_conv3d_centered(torch.from_numpy(x), torch.from_numpy(weights), torch.from_numpy(bias),
                        stride=stride, padding=padding).numpy()
                error = float(np.max(np.abs(new-reference))); tolerance = 3e-6 if dtype == np.float32 else 1e-7
                r['cases'].append(dict(case='stride_padding', dtype=np.dtype(dtype).name, stride=list(stride), padding=list(padding),
                    output_shape=list(new.shape), output_dtype=str(new.dtype), centered_max_error=error, strict_tolerance=tolerance,
                    all_outputs_finite=bool(np.isfinite(new).all()), strict_gate_passed=error <= tolerance and np.isfinite(new).all().item()))
        r['derivatives'] = []
        for dtype in (np.float64, np.float32):
            x, weights, bias = [np.asarray(v, dtype=dtype) for v in (examples[0][1][:1], w, b)]
            tensors = [torch.from_numpy(v.copy()).requires_grad_() for v in (x, weights, bias)]
            y = local_kernel_conv3d_centered(*tensors); y[0, 1, 3, 3, 3].backward()
            if dtype == np.float32:
                doubles = [torch.from_numpy(v.astype(np.float64)).requires_grad_() for v in (x, weights, bias)]
                local_kernel_conv3d_centered(*doubles)[0, 1, 3, 3, 3].backward()
                errors = [float((a.grad.double()-c.grad).abs().max()) for a, c in zip(tensors, doubles)]
                r['derivatives'].append(dict(dtype='float32', reference='same_quantized_values_float64_autograd',
                    max_error_input_weight_bias=errors, strict_gate_passed=max(errors) <= 3e-6))
            else:
                for which, index in [(0, (0, 2, 3, 3, 3)), (1, (1, 1, 1, 1, 1)), (2, (1,))]:
                    values = [v.copy() for v in (x, weights, bias)]; h = 1e-5
                    values[which][index] += h; plus = explicit(*values)[0, 1, 3, 3, 3]
                    values[which][index] -= 2*h; minus = explicit(*values)[0, 1, 3, 3, 3]
                    analytical = float(tensors[which].grad[index]); numerical = float((plus-minus)/(2*h))
                    error = abs(analytical-numerical)
                    r['derivatives'].append(dict(dtype='float64', variable=['input', 'weight', 'bias'][which],
                        autograd=analytical, finite_difference=numerical, absolute_error=error, strict_gate_passed=error <= 1e-7))
        r['locality'] = []
        for dtype in (np.float64, np.float32):
            image = rng.normal(size=(1, 3, 12, 12, 12)).astype(dtype)
            crop = image[:, :, 2:10, 2:10, 2:10].copy(); changed = image.copy(); changed[0, 2, 11, 11, 11] += 20
            weights, bias = [np.asarray(v, dtype=dtype) for v in (w, b)]
            with torch.inference_mode():
                full, small, perturbed = [local_kernel_conv3d_centered(torch.from_numpy(v), torch.from_numpy(weights),
                    torch.from_numpy(bias)).numpy() for v in (image, crop, changed)]
            interior = full[:, :, 3:9, 3:9, 3:9]
            crop_error = float(np.max(np.abs(interior-small[:, :, 1:7, 1:7, 1:7])))
            remote_error = float(np.max(np.abs(interior-perturbed[:, :, 3:9, 3:9, 3:9])))
            tol = 1e-12 if dtype == np.float64 else 3e-6
            r['locality'].append(dict(dtype=np.dtype(dtype).name, crop_error=crop_error, remote_error=remote_error,
                strict_gate_passed=crop_error <= tol and remote_error == 0))
        for name in ('float32', 'float64'):
            r[name+'_qualification_passed'] = all(row['strict_gate_passed'] for key in ('cases', 'derivatives', 'locality')
                for row in r[key] if row['dtype'] == name)
        assert sha(source) == r['original_result_sha256']; r['original_failure_preserved'] = True
        r['cuda_initialized'] = torch.cuda.is_initialized(); assert not r['cuda_initialized']
        assert time.perf_counter()-started <= 120
        r['resources_after'] = resource_guard(); r['complete'] = True
    except Exception as e:
        r['errors'].append(type(e).__name__+': '+str(e)); r['traceback'] = traceback.format_exc()
    r['elapsed_seconds'] = time.perf_counter()-started; r['finished_utc'] = datetime.now(timezone.utc).isoformat(); save()
    assert path.stat().st_size < 1_000_000
    print(json.dumps({k:r.get(k) for k in ('complete', 'errors', 'float32_qualification_passed', 'float64_qualification_passed',
        'elapsed_seconds', 'cuda_initialized')}), flush=True)
    return int(not r['complete'])

if __name__ == '__main__': raise SystemExit(main())
