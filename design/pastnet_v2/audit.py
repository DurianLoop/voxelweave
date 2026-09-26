"""Read-only v1 evidence audit. Target-assisted probes are diagnostics, never model inputs."""
from __future__ import annotations

import argparse
from pathlib import Path

import nibabel as nib
import numpy as np
import torch
from skimage.registration import optical_flow_tvl1
from skimage.transform import resize, warp

from fastmri_brain_pastnet_2p5d.data import build_ma3c_interval_sample
from fastmri_brain_pastnet_2p5d.model_ma3aggressive import PASTNetMA3Aggressive2p5D
from .common import G086, PACKAGE, ROOT, fastmri_records, read_csv, sha256, write_csv, write_json


def bands(x):
    h, w = x.shape[-2:]
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    radius = np.sqrt(fy * fy + fx * fx)
    spec = np.fft.fft2(x, norm='ortho')
    return [np.fft.ifft2(spec * mask, norm='ortho').real for mask in
            (radius < .10, (radius >= .10) & (radius < .28), radius >= .28)]


def error_stats(pred, target):
    err = pred - target
    squared = err.ravel() ** 2
    mse = float(squared.mean())
    energies = [float((b * b).mean()) for b in bands(err)]
    edge = np.hypot(*np.gradient(target))
    mask = edge >= np.quantile(edge, .9)
    return dict(mse=mse, psnr=-10 * np.log10(max(mse, 1e-12)), mae=float(np.abs(err).mean()),
                low_mse=energies[0], mid_mse=energies[1], high_mse=energies[2],
                tail10_energy_share=float(np.sort(squared)[-max(1, len(squared)//10):].sum() / max(squared.sum(), 1e-12)),
                edge_mse=float((err[mask] ** 2).mean()))


def target_assisted_alignment(anchor, target):
    # Fixed non-learning registration probe. Failure is not an information upper bound.
    small_a = resize(anchor, (96, 96), anti_aliasing=True, preserve_range=True)
    small_t = resize(target, (96, 96), anti_aliasing=True, preserve_range=True)
    flow = optical_flow_tvl1(small_t, small_a, num_warp=5, num_iter=10)
    h, w = target.shape
    flow = np.stack([resize(flow[0], (h, w), preserve_range=True) * h / 96,
                     resize(flow[1], (h, w), preserve_range=True) * w / 96])
    yy, xx = np.meshgrid(np.arange(h), np.arange(w), indexing='ij')
    return warp(anchor, np.array([yy + flow[0], xx + flow[1]]), mode='edge', preserve_range=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=PACKAGE / 'results/audit_validation')
    parser.add_argument('--limit', type=int)
    parser.add_argument('--skip-alignment', action='store_true')
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError(f'Use a new audit output directory: {args.out}')
    records = [r for r in fastmri_records() if r['split'] == 'val'][:args.limit]
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    torch.set_num_threads(4)
    ckpt = torch.load(G086, map_location='cpu', weights_only=False)
    model = PASTNetMA3Aggressive2p5D(**ckpt['model_config']).to(device).eval()
    model.load_state_dict(ckpt['model_state_dict'], strict=True)
    rows, domain = [], []
    for i, rec in enumerate(records):
        image = nib.load(rec['path'])
        raw = image.get_fdata(dtype=np.float32)
        v = (raw - raw.min()) / max(float(raw.max() - raw.min()), 1e-8)
        v = resize(v, (256, 256, v.shape[2]), preserve_range=True, anti_aliasing=True).astype(np.float32)
        sparse = v[:, :, ::4]
        domain.append(dict(case_id=rec['case_id'], dataset='fastmri', depth=v.shape[2],
                           sparse_anchors=sparse.shape[2], header_spacing=str(image.header.get_zooms()),
                           orientation_trust='synthetic_diagonal_NOT_patient_orientation',
                           raw_min=float(raw.min()), raw_max=float(raw.max()),
                           adjacent_change=float(np.abs(np.diff(v, axis=2)).mean()),
                           sparse_change=float(np.abs(np.diff(sparse, axis=2)).mean()),
                           sparse_min=float(sparse.min()), sparse_max=float(sparse.max())))
        for z in range(0, v.shape[2] - 4, 4):
            sample = build_ma3c_interval_sample(v, z)
            cond = torch.from_numpy(sample['cond_ma_stack'])[None].to(device)
            with torch.no_grad(), torch.autocast(device.type, enabled=device.type == 'cuda'):
                pred = model(cond).float().clamp(0, 1)[0, :, 0].cpu().numpy()
            for j, q in enumerate((.25, .5, .75)):
                target = v[:, :, z+j+1]
                left, right = v[:, :, z], v[:, :, z+4]
                coarse = (1-q)*left + q*right
                four = v[:, :, [max(0, z-4), z, z+4, min((v.shape[2]-1)//4*4, z+8)]]
                six_idx = [k for k in range(z-8, z+13, 4) if 0 <= k < v.shape[2]]
                six = v[:, :, six_idx]
                probes = dict(g086=pred[j], linear=coarse,
                              oracle_four_envelope=np.clip(target, four.min(2), four.max(2)),
                              oracle_six_envelope=np.clip(target, six.min(2), six.max(2)),
                              diagnostic_nearer_real=.5*(v[:, :, z+j] + v[:, :, z+j+2]),
                              oracle_target_lowres=coarse + bands(target-coarse)[0])
                if not args.skip_alignment:
                    probes['oracle_tvl1_target_alignment'] = ((1-q)*target_assisted_alignment(left, target)
                                                               + q*target_assisted_alignment(right, target))
                for method, value in probes.items():
                    rows.append(dict(case_id=rec['case_id'], z=z, phase=q, method=method,
                                     **error_stats(value, target)))
        print(f'audit validation {i+1}/{len(records)} {rec["case_id"]}', flush=True)
    write_csv(args.out / 'per_slice.csv', rows)
    write_csv(args.out / 'domain_validation.csv', domain)
    import pandas as pd
    df = pd.DataFrame(rows)
    metric_columns = list(error_stats(np.zeros((8, 8)), np.zeros((8, 8))))
    per_case = df.groupby(['case_id', 'method'])[metric_columns].mean().reset_index()
    per_case.to_csv(args.out / 'per_case.csv', index=False)
    summary = per_case.groupby('method').mean(numeric_only=True).reset_index()
    summary.to_csv(args.out / 'summary.csv', index=False)
    df.groupby(['method', 'phase']).mean(numeric_only=True).drop(columns='z').to_csv(args.out / 'phase.csv')
    evidence = {}
    for name in ('full_pastnet_g078_latent_multiscale160', 'full_pastnet_g079_tail_aware160',
                 'full_pastnet_g084_dual_domain140', 'full_pastnet_g086_dual_restart60'):
        p = ROOT / 'design/fastmri_brain_pastnet_2p5d/runs' / name / 'metrics/summary_metrics.csv'
        if p.exists():
            evidence[name] = dict(path=str(p), sha256=sha256(p), rows=read_csv(p))
    write_json(args.out / 'manifest.json', dict(split='val', cases=len(records), complete_validation=args.limit is None,
        checkpoint_sha256=sha256(G086), target_assisted_probes_are_not_deployable=True,
        probes_are_not_bounds_on_Bayes_error=True, metric='mean missing-slice PSNR, normalized range 1, 256 square',
        test_not_loaded=True, existing_development_evidence=evidence))
    print(summary.to_string(index=False), flush=True)


if __name__ == '__main__':
    main()
