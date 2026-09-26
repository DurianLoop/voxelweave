"""Plan-9 Local Physical Measurement Influence for SAINT, I3Net and CycleINR.

Protocol sources:
  UNIFIED_INFLUENCE_PROTOCOL.md
  INFLUENCE_SAMPLING_ADDENDUM.md
"""
from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats
from skimage.transform import resize
import torch

HERE = Path(__file__).resolve()
P9 = HERE.parents[1]
PAPER = P9.parent
ROOT = PAPER.parents[1]
OUT = P9 / "outputs"
sys.path[:0] = [str(ROOT / "baseline"), str(ROOT / "pre"), str(ROOT / "design"), str(ROOT)]

SEEDS = (6101, 6102, 6103, 6104)
SETTINGS = {"primary": 0.01, "eps005": 0.005, "eps020": 0.02, "negative": -0.01}
PAIR_REF = (-2, 2)
PAIR_CONTEXTS = [PAIR_REF, (-2, 1), (-2, 3), (-1, 2), (-3, 2), (-1, 1), (-1, 3), (-3, 1), (-3, 3)]
FOUR_REF = (-5, -1, 3, 7)
FOUR_CONTEXTS = [
    FOUR_REF, (-9, -5, -1, 3), (-1, 3, 7, 11),
    (-10, -6, -2, 2), (-7, -3, 1, 5), (-6, -2, 2, 6),
    (-3, 1, 5, 9), (-2, 2, 6, 10),
]


def rho(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 5 or np.std(a[ok]) == 0 or np.std(b[ok]) == 0:
        return float("nan")
    return float(stats.spearmanr(a[ok], b[ok]).statistic)


def load_cases(model: str, max_cases: int | None):
    if model == "saint":
        ids = [x.strip() for x in (ROOT / "dataset/fastMRI_brain_T2/processed/splits/nifti_seed3407/test_cases.txt").read_text(encoding="utf-8").splitlines() if x.strip()]
        paths = [ROOT / "dataset/fastMRI_brain_T2/processed/nifti" / (x if x.endswith(".nii.gz") else x + ".nii.gz") for x in ids]
        return [(p.name.removesuffix(".nii.gz"), p) for p in paths[:max_cases]] if max_cases else [(p.name.removesuffix(".nii.gz"), p) for p in paths]
    ids = [x.strip() for x in (ROOT / "dataset/IXI/splits/seed3407/test_cases.txt").read_text(encoding="utf-8").splitlines() if x.strip()]
    meta = pd.read_csv(ROOT / "dataset/IXI/metadata/ixi_cases.csv").set_index("case_id")
    rows = []
    for case in ids:
        p = Path(meta.loc[case, "T2_path"])
        depth = nib.load(str(p)).shape[2]
        if depth >= 23:
            rows.append((case, p))
        if len(rows) == (max_cases or 24):
            break
    return rows


def patterns():
    out = []
    for seed in SEEDS:
        q = np.random.default_rng(seed).choice([-1.0, 1.0], size=(256, 256)).astype(np.float32)
        q -= q.mean()
        out.append(q)
    return out


def paired_metrics(a, b, y):
    ea = (a - y).astype(np.float64); eb = (b - y).astype(np.float64)
    n1 = float(ea @ ea); n2 = float(eb @ eb); total = 0.5 * (n1 + n2)
    shared = float(np.sum(((ea + eb) / 2.0) ** 2)); obs = float(np.sum(((ea - eb) / 2.0) ** 2))
    return {
        "error_cosine": float(ea @ eb / np.sqrt(n1 * n2)) if n1 > 0 and n2 > 0 else np.nan,
        "shared_fraction": shared / total if total > 0 else np.nan,
        "observable_fraction": obs / total if total > 0 else np.nan,
        "disagreement_mae": float(np.mean(np.abs(a - b))),
        "paired_error_mae": float(0.5 * (np.mean(np.abs(ea)) + np.mean(np.abs(eb)))),
    }


def influence(ref_resp, alt_resp, ref_positions, alt_positions, setting):
    shared = set(ref_positions) & set(alt_positions)
    if not shared:
        return 0.0, 0.0
    dot = na = nb = common = 0.0
    for k in range(len(SEEDS)):
        for pos in ref_positions:
            v = ref_resp[(setting, pos, k)]; na += float(v @ v)
        for pos in alt_positions:
            v = alt_resp[(setting, pos, k)]; nb += float(v @ v)
        for pos in shared:
            a = ref_resp[(setting, pos, k)]; b = alt_resp[(setting, pos, k)]
            dot += float(a @ b); common += min(float(np.linalg.norm(a)), float(np.linalg.norm(b)))
    cosine = dot / np.sqrt(na * nb) if na > 0 and nb > 0 else 0.0
    mass = common / (0.5 * (np.sqrt(na) + np.sqrt(nb))) if na + nb > 0 else 0.0
    return cosine, mass


class Runner:
    def __init__(self, model, device):
        self.name = model; self.device = torch.device(device)
        if model == "saint":
            from ixi_diffusion.saint import SAINTInterpolator
            ck = ROOT / "baseline/fastmri_brain_t2_saint_expanded/runs/full/checkpoints/saint_epoch_best.pth"
            self.wrapper = SAINTInterpolator(ck, device=device)
        elif model == "i3net":
            from ixi_i3net.train import I3NetInterpolator
            ck = ROOT / "baseline/ixi_i3net/runs/full_test115_stable/checkpoints/i3net_epoch_best.pth"
            self.wrapper = I3NetInterpolator(ck, device=device, label="Plan9-IXI")
        else:
            from ixi_arssr.inference import ArSSRInterpolator
            ck = ROOT / "baseline/ixi_cycleinr/runs/full/checkpoints/cycleinr_epoch_best.pth"
            self.wrapper = ArSSRInterpolator(ck, device=device, query_chunk=65536)
        self.net = self.wrapper.model

    def _forward_saint(self, arr, target_index, z_abs, chunk=16):
        ys = []
        for i in range(0, len(arr), chunk):
            x = torch.from_numpy(np.stack(arr[i:i+chunk])).float().to(self.device)
            with torch.no_grad(), torch.amp.autocast(device_type=self.device.type, enabled=self.device.type == "cuda"):
                q = self.net(x).float().clamp(0, 1)[:, 0]
            ys.extend(q.cpu().numpy())
        return ys

    def _forward_i3net(self, arr, target_index, z_abs, chunk=8):
        ys = []
        for i in range(0, len(arr), chunk):
            x = torch.from_numpy(np.stack(arr[i:i+chunk])).float().to(self.device)
            with torch.no_grad(), torch.amp.autocast(device_type=self.device.type, enabled=self.device.type == "cuda"):
                q = self.net(x).float().clamp(0, 1)[..., target_index]
            ys.extend(q.cpu().numpy())
        return ys

    def _forward_cycle(self, arr, target_index, z_abs, mask, chunk=6):
        yy, xx = np.where(mask)
        coords = np.stack([
            xx.astype(np.float32) / 255.0 * 2 - 1,
            yy.astype(np.float32) / 255.0 * 2 - 1,
            np.full(len(xx), z_abs, np.float32),
        ], axis=1)
        ys = []
        for i in range(0, len(arr), chunk):
            dense = np.stack(arr[i:i+chunk])[:, None]
            x = torch.from_numpy(dense).float().to(self.device)
            c = torch.from_numpy(np.repeat(coords[None], len(dense), axis=0)).float().to(self.device)
            with torch.no_grad(), torch.amp.autocast(device_type=self.device.type, enabled=self.device.type == "cuda"):
                q = self.net(x, c).float().clamp(0, 1)[..., 0]
            ys.extend(q.cpu().numpy())
        return ys

    def context(self, norm, z, ctx, mask, pats):
        anchors = [resize(norm[:, :, z + o], (256, 256), preserve_range=True, anti_aliasing=True).astype(np.float32) for o in ctx]
        target_index = -ctx[0]
        records = [("base", None, None, 0.0)]
        for setting, eps in SETTINGS.items():
            for ai, pos in enumerate(ctx):
                for k in range(len(SEEDS)):
                    records.append((setting, ai, k, eps))
        inputs = []
        if self.name == "saint":
            rel = float(-ctx[0]) / float(ctx[1] - ctx[0])
            z_abs = float(z) / max(float(norm.shape[2] - 1), 1.0)
            yy = self.wrapper.y_map; xx = self.wrapper.x_map
            for setting, ai, k, eps in records:
                aa = [q.copy() for q in anchors]
                if ai is not None: aa[ai] = np.clip(aa[ai] + eps * pats[k], 0, 1)
                inputs.append(np.stack([aa[0], aa[1], np.full((256,256), rel, np.float32), np.full((256,256), z_abs, np.float32), yy, xx]))
            pred = self._forward_saint(inputs, target_index, z_abs)
        elif self.name == "i3net":
            z_abs = target_index / 12.0 * 2 - 1
            for setting, ai, k, eps in records:
                aa = [q.copy() for q in anchors]
                if ai is not None: aa[ai] = np.clip(aa[ai] + eps * pats[k], 0, 1)
                inputs.append(np.stack(aa, axis=-1))
            pred = self._forward_i3net(inputs, target_index, z_abs)
        else:
            z_abs = target_index / 12.0 * 2 - 1
            for setting, ai, k, eps in records:
                aa = [q.copy() for q in anchors]
                if ai is not None: aa[ai] = np.clip(aa[ai] + eps * pats[k], 0, 1)
                dense = np.zeros((13, 256, 256), np.float32)
                for j, q in enumerate(aa): dense[j * 4] = q
                for j in range(3):
                    for off in range(1, 4): dense[j*4+off] = (1-off/4)*aa[j] + (off/4)*aa[j+1]
                inputs.append(dense)
            pred = self._forward_cycle(inputs, target_index, z_abs, mask)
        base = pred[0][mask] if self.name != "cycleinr" else pred[0]
        responses = {}
        for rec, q in zip(records[1:], pred[1:]):
            setting, ai, k, _ = rec
            v = q[mask] if self.name != "cycleinr" else q
            responses[(setting, z + ctx[ai], k)] = (v - base).astype(np.float32)
        return base.astype(np.float32), responses


def one_case(runner, gt, z):
    lo = float(np.nanmin(gt)); hi = float(np.nanmax(gt)); scale = hi - lo
    norm = ((gt - lo) / (scale + 1e-8)).astype(np.float32)
    y2 = resize(norm[:, :, z], (256, 256), preserve_range=True, anti_aliasing=True).astype(np.float32)
    mask = np.abs(y2) > 0.01 * max(float(np.max(np.abs(y2))), 1e-6)
    y = y2[mask]
    pats = patterns(); contexts = PAIR_CONTEXTS if runner.name == "saint" else FOUR_CONTEXTS
    ref = PAIR_REF if runner.name == "saint" else FOUR_REF
    preds = {}; responses = {}
    for ctx in contexts:
        preds[ctx], responses[ctx] = runner.context(norm, z, ctx, mask, pats)
    rows = []
    for ctx in contexts:
        rec = {
            "context": str(ctx), "overlap_count": len(set(ref) & set(ctx)),
            "span": ctx[-1] - ctx[0], "asymmetry": abs(ctx[0] + ctx[-1]),
            **paired_metrics(preds[ref] * scale + lo, preds[ctx] * scale + lo, y * scale + lo),
        }
        for setting in SETTINGS:
            c, m = influence(responses[ref], responses[ctx], [z+v for v in ref], [z+v for v in ctx], setting)
            rec[f"influence_{setting}"] = c; rec[f"common_mass_{setting}"] = m
        rows.append(rec)
    return rows


def summarize(x, bootstrap=2000):
    endpoints = ["error_cosine", "shared_fraction", "observable_fraction", "disagreement_mae"]
    rows = []; rng = np.random.default_rng(20260814)
    for model, allg in x.groupby("model"):
        g = allg[allg.context != allg.reference_context].copy()
        for ep in endpoints:
            rc = rho(g.overlap_count, g[ep]); ri = rho(g.influence_primary, g[ep]); point = abs(ri) - abs(rc)
            reps = []
            clusters = g.patient_cluster.unique(); by = {c:g[g.patient_cluster == c] for c in clusters}
            for _ in range(bootstrap):
                b = pd.concat([by[c] for c in rng.choice(clusters, len(clusters), replace=True)], ignore_index=True)
                reps.append(abs(rho(b.influence_primary, b[ep])) - abs(rho(b.overlap_count, b[ep])))
            rows.append({"model":model,"endpoint":ep,"rho_overlap":rc,"rho_influence":ri,"delta_abs_rho":point,
                         "ci_low":float(np.nanquantile(reps,.025)),"ci_high":float(np.nanquantile(reps,.975)),
                         "cases":int(g.case.nunique()),"planes":int(g[["case","z"]].drop_duplicates().shape[0])})
        fixed = g[g.overlap_count > 0]
        for ep in endpoints:
            rows.append({"model":model,"endpoint":"fixed_nonzero_"+ep,"rho_overlap":np.nan,
                         "rho_influence":rho(fixed.influence_primary,fixed[ep]),"delta_abs_rho":np.nan,
                         "ci_low":np.nan,"ci_high":np.nan,"cases":int(fixed.case.nunique()),
                         "planes":int(fixed[["case","z"]].drop_duplicates().shape[0])})
    summary = pd.DataFrame(rows)
    stable = []
    for model, g in x.groupby("model"):
        g = g[(g.context != g.reference_context) & (g.overlap_count > 0)]
        for setting in ("eps005","eps020","negative"):
            rr = rho(g.influence_primary, g[f"influence_{setting}"])
            stable.append({"model":model,"setting":setting,"rho":rr,"pass":bool(np.isfinite(rr) and rr >= .90),"configurations":len(g)})
    return summary, pd.DataFrame(stable)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--model", choices=["saint","i3net","cycleinr"], required=True)
    ap.add_argument("--device", default="cuda"); ap.add_argument("--max-cases", type=int); ap.add_argument("--bootstrap", type=int, default=2000)
    a = ap.parse_args(); OUT.mkdir(parents=True, exist_ok=True)
    cases = load_cases(a.model, a.max_cases); runner = Runner(a.model, a.device); rows = []; t0 = time.perf_counter()
    ref = PAIR_REF if a.model == "saint" else FOUR_REF
    for i, (case, path) in enumerate(cases, 1):
        gt = nib.load(str(path)).get_fdata(dtype=np.float32)
        if a.model == "saint":
            zs = sorted(set(int(round(v)) for v in np.linspace(3, gt.shape[2]-4, 5)[1:-1]))
        else:
            zs = [int(np.clip(gt.shape[2] // 2, 10, gt.shape[2]-12))]
        for z in zs:
            for q in one_case(runner, gt, z):
                rows.append({"dataset":"fastmri" if a.model=="saint" else "ixi","case":case,"patient_cluster":case,
                             "model":a.model,"z":z,"reference_context":str(ref),**q})
        print(f"P9 influence {a.model} {i}/{len(cases)} {case} planes={len(zs)} elapsed={time.perf_counter()-t0:.1f}s", flush=True)
    x = pd.DataFrame(rows); x.to_csv(OUT / f"p9_influence_{a.model}_per_case_config.csv", index=False)
    s, st = summarize(x, a.bootstrap); s.to_csv(OUT / f"p9_influence_{a.model}_summary.csv", index=False); st.to_csv(OUT / f"p9_influence_{a.model}_stability.csv", index=False)
    payload = {"model":a.model,"cases":len(cases),"rows":len(x),"elapsed_seconds":time.perf_counter()-t0,
               "all_stability_gates_pass":bool(st["pass"].all()),"sampling_addendum":"INFLUENCE_SAMPLING_ADDENDUM.md"}
    (OUT / f"p9_influence_{a.model}.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(s.to_string(index=False)); print(st.to_string(index=False)); print(json.dumps(payload, indent=2))
    del runner; gc.collect()
    if torch.cuda.is_available(): torch.cuda.empty_cache()


if __name__ == "__main__": main()
