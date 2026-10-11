"""Post-result convex two-guard oracle, with fixed coefficients and numerical certificates."""
from __future__ import annotations

import json
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
import numpy as np
from scipy.optimize import minimize
from vs_seg_task_cpu_support import ROOT, resource_gate
from vs_seg_full_volume_runtime import sha
import verify_mc_rc_three_development_action_oracle as independent_three
import verify_mc_rc_001_002_raw_action_oracle as independent_two

OUT = ROOT / "experiments/mc_rc_five_developer_constrained_oracle"
PLAN = ROOT / "MC_RC_FIVE_DEVELOPER_CONSTRAINED_ORACLE_PLAN_2026-10-02.md"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, allow_nan=False, indent=2) + "\n", encoding="utf-8")


def collect():
    patients, paths = [], [PLAN, Path(__file__), Path(independent_three.__file__), Path(independent_two.__file__), ROOT / "experiments/vs_seg_task_cpu_support.py"]
    for folder, helper in [("mc_rc_three_development_action_oracle", independent_three), ("mc_rc_001_002_raw_action_oracle", independent_two)]:
        base = ROOT / "experiments" / folder
        contract, result, proof = read(base / "run_contract.json"), read(base / "attempt_01.json"), read(base / "independent_numerical_and_forward_verification.json")
        if not result["complete"] or proof["errors"] or proof["result_sha256"] != sha(base / "attempt_01.json"):
            raise ValueError("Complete independent developer inputs required")
        paths.extend([base / "run_contract.json", base / "attempt_01.json", base / "independent_numerical_and_forward_verification.json"])
        by_patient = {r["patient"]: r for r in result["patients"]}
        for case in contract["cases"]:
            saved = by_patient[case["patient"]]
            action = next(a for a in saved["actions"] if a["base"] == "raw_pchip")
            if sha(ROOT / saved["hat_file"]) != saved["hat_sha256"]:
                raise ValueError("Saved HAT output differs")
            patients.append((case, saved, action, helper, base / "run_contract.json"))
            paths.extend([ROOT / saved["hat_file"], ROOT / case["header"]["transfer"]["file"], ROOT / case["label"]["label_file"]])
    patients.sort(key=lambda x: x[0]["patient"])
    if [p[0]["patient"] for p in patients] != ["VS-MC-RC-001", "VS-MC-RC-002", "VS-MC-RC-004", "VS-MC-RC-005", "VS-MC-RC-006"]:
        raise ValueError("Fixed-five developer roster differs")
    frozen = {"created_utc": datetime.now(timezone.utc).isoformat(), "patients": [p[0]["patient"] for p in patients], "post_result_diagnostic": True,
              "original_unconstrained_raw_gate_passed": False, "independent_confirmation": False,
              "files": [{"path": p.relative_to(ROOT.parent).as_posix(), "sha256": sha(p), "bytes": p.stat().st_size} for p in sorted(set(paths))]}
    write(OUT / "run_contract.json", frozen)
    return patients


def coefficients(case, saved, action, helper):
    native, label = helper.raw_source(case)
    with np.load(ROOT / saved["hat_file"]) as bundle:
        hat = bundle["image_rcz"]
    observations, targets = saved["observation_indices"], saved["targets"]
    observed = native[:, :, observations]
    span = float(observed.max()) - float(observed.min())
    anchors = [observed[:, :, i] for i in range(len(observations))]
    lesion_targets = action["summaries"]["fixed_0"]["lesion"]["nonempty_targets"]
    total_lesion = action["summaries"]["fixed_0"]["lesion"]["pixels"]
    if not lesion_targets or not total_lesion:
        raise ValueError("Empty lesion endpoint; no guard manufactured")
    rows, keys = [], []
    for z in targets:
        i, t = z // 4, z % 4 / 4
        base = helper.hermite_plane(anchors, i, t).astype(np.float32)
        left, right = anchors[i], anchors[i + 1]
        support = (abs(left) > .01 * max(float(abs(left).max()), 1e-6)) | (abs(right) > .01 * max(float(abs(right).max()), 1e-6))
        roi = support & label[:, :, z]
        e = (native[:, :, z].astype(float) - base) / span
        delta = (hat[:, :, z].astype(float) - base) / span
        b0, m0, d0 = helper.block_sum(e * e * support), helper.block_sum(e * delta * support), helper.block_sum(delta * delta * support)
        br, mr, dr = helper.block_sum(e * e * roi), helper.block_sum(e * delta * roi), helper.block_sum(delta * delta * roi)
        counts = helper.block_sum(support.astype(int))
        factor_s = int(support.sum()) * len(targets)
        factor_e = int(roi.sum()) * lesion_targets
        for rr, cc in np.argwhere(counts > 0):
            raw = [b0[rr, cc], m0[rr, cc], d0[rr, cc]]
            lesion = [br[rr, cc], mr[rr, cc], dr[rr, cc]]
            row = [v / factor_s for v in raw]
            row.extend([v / factor_e if factor_e else 0. for v in lesion])
            row.extend([v / total_lesion for v in lesion])
            rows.append(row)
            keys.append([z, int(rr * 32), int(cc * 32)])
    coef = np.array(rows, dtype=float)
    def losses(alpha):
        return np.array([np.sum(coef[:, offset] - 2 * coef[:, offset + 1] * alpha + coef[:, offset + 2] * alpha * alpha) for offset in (0, 3, 6)])
    zero, one = losses(np.zeros(len(coef))), losses(np.ones(len(coef)))
    unconstrained_alpha = np.divide(coef[:, 1], coef[:, 2], out=np.zeros(len(coef)), where=coef[:, 2] != 0).clip(0, 1)
    un = losses(unconstrained_alpha)
    for computed, name in [(zero, "fixed_0"), (one, "fixed_1"), (un, "tile_32_oracle")]:
        sm = action["summaries"][name]
        expected = [sm["support"]["target_equal_nmse"], sm["lesion"]["target_equal_nmse"], sm["lesion"]["pixel_weighted_nmse"]]
        if not np.allclose(computed, expected, rtol=1e-7, atol=1e-10):
            raise ValueError("Frozen endpoint coefficient reconstruction differs " + name)
    return coef, np.array(keys, dtype=int), zero, one, un, unconstrained_alpha


def solve(coef, limits):
    def alpha_at(lam):
        m = coef[:, 1] + lam[0] * coef[:, 4] + lam[1] * coef[:, 7]
        d = coef[:, 2] + lam[0] * coef[:, 5] + lam[1] * coef[:, 8]
        return np.divide(m, d, out=np.zeros_like(m), where=d != 0).clip(0, 1)
    def losses(alpha):
        return np.array([np.sum(coef[:, offset] - 2 * coef[:, offset + 1] * alpha + coef[:, offset + 2] * alpha ** 2) for offset in (0, 3, 6)])
    def dual(lam):
        alpha = alpha_at(lam)
        value = losses(alpha)
        violation = value[1:] - limits
        return -(value[0] + np.dot(lam, violation)), -violation
    opt = minimize(dual, np.zeros(2), method="L-BFGS-B", jac=True, bounds=[(0, None), (0, None)], options={"maxiter": 2000, "maxls": 50, "ftol": 1e-15, "gtol": 1e-12})
    lam = np.array(opt.x, dtype=float)
    alpha = alpha_at(lam)
    value = losses(alpha)
    violations = value[1:] - limits
    dual_value = float(value[0] + np.dot(lam, violations))
    gap = float(value[0] - dual_value)
    gradient = 2 * ((coef[:, 2] + lam[0] * coef[:, 5] + lam[1] * coef[:, 8]) * alpha - (coef[:, 1] + lam[0] * coef[:, 4] + lam[1] * coef[:, 7]))
    projected = np.where(alpha == 0, np.minimum(gradient, 0), np.where(alpha == 1, np.maximum(gradient, 0), gradient))
    stationarity = float(abs(projected).max())
    certified = bool(np.isfinite(value).all() and np.isfinite(lam).all() and np.isfinite(alpha).all() and (alpha >= 0).all() and (alpha <= 1).all() and (violations <= 1e-10).all() and -1e-10 <= gap <= 1e-8 and stationarity <= 1e-8)
    return alpha, {"multipliers": lam.tolist(), "optimizer_success": bool(opt.success), "optimizer_message": str(opt.message), "iterations": int(opt.nit), "losses_support_lesion_equal_lesion_pixel": value.tolist(), "lesion_limits": limits.tolist(), "violations": violations.tolist(), "primal_objective": float(value[0]), "dual_lower_bound": dual_value, "primal_dual_gap": gap, "max_box_stationarity_residual": stationarity, "numerically_certified": certified}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    resource_gate()
    OUT.mkdir(parents=True, exist_ok=False)
    cases = collect()
    rows = []
    for case, saved, action, helper, source_contract in cases:
        resource_gate()
        coef, keys, zero, one, un, un_alpha = coefficients(case, saved, action, helper)
        limits = np.minimum(zero[1:], one[1:])
        alpha, solution = solve(coef, limits)
        path = OUT / (case["patient"] + "_coefficients_and_alpha.npz")
        np.savez_compressed(path, coefficients=coef, tile_z_row_col=keys, constrained_alpha=alpha, unconstrained_alpha=un_alpha, lesion_limits=limits)
        gain = 10 * math.log10(min(zero[0], one[0]) / solution["primal_objective"])
        row = {"patient": case["patient"], "source_contract": source_contract.relative_to(ROOT).as_posix(), "targets": len(saved["targets"]), "tiles": len(coef),
               "coefficients_file": path.relative_to(ROOT).as_posix(), "coefficients_sha256": sha(path), "baseline_losses": zero.tolist(), "candidate_losses": one.tolist(),
               "unconstrained_losses": un.tolist(), "unconstrained_original_gate_passed": action["development_gate_passed"],
               "solution": solution, "constrained_support_gain_db_vs_better_fixed": gain,
               "post_result_constrained_space_gate_passed": solution["numerically_certified"] and gain >= .1,
               "independent_confirmation": False}
        rows.append(row)
        print(json.dumps({"patient": case["patient"], "gain_db": gain, "certified": solution["numerically_certified"], "violations": solution["violations"], "gap": solution["primal_dual_gap"], "post_result_space_gate": row["post_result_constrained_space_gate_passed"]}), flush=True)
    result = {"created_utc": datetime.now(timezone.utc).isoformat(), "complete": len(rows) == 5, "run_contract_sha256": sha(OUT / "run_contract.json"), "patients": rows,
              "post_result_diagnostic": True, "all_five_constrained_space_gate_passed": all(r["post_result_constrained_space_gate_passed"] for r in rows),
              "original_unconstrained_raw_gate_passed": False, "task_fidelity_evaluated": False, "gpu_used": False, "scientific_independent_validation_patients": 0, "publication_claim_confirmed": False}
    write(OUT / "attempt_01.json", result)
    print(json.dumps({"complete": result["complete"], "all_five_constrained_space_gate_passed": result["all_five_constrained_space_gate_passed"], "original_unconstrained_raw_gate_passed": False}), flush=True)


if __name__ == "__main__":
    main()
