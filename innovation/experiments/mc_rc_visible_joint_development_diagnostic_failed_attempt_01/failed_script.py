"""Fixed five-patient LOPO visible-feature / joint-risk development diagnostic.

Features take only observed anchors, fixed candidates and acquisition fields.
Hidden reference and manual label enter supervision/evaluation separately.
"""
from __future__ import annotations
import hashlib
import json
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
import numpy as np
from scipy.interpolate import PchipInterpolator
from vs_seg_task_cpu_support import ROOT, resource_gate
from verify_mc_rc_five_developer_constrained_oracle import source

OUT = ROOT / "experiments/mc_rc_visible_joint_development_diagnostic"
PLAN = ROOT / "MC_RC_VISIBLE_JOINT_DEVELOPMENT_DIAGNOSTIC_PLAN_2026-10-02.md"
ORACLE = ROOT / "experiments/mc_rc_five_developer_constrained_oracle"
GRID = np.array([0., .25, .5, .75, 1.])
RIDGE = .01
FEATURES = ["phase", "phase_squared", "relative_z", "relative_row", "relative_col", "rows_over_256", "cols_over_256", "spacing_row_mm", "spacing_col_mm", "spacing_plane_mm", "observed_gap_mm", "slice_thickness_mm", "slice_thickness_missing", "support_fraction",
            "left_mean", "right_mean", "base_mean", "candidate_mean", "left_std", "right_std", "base_std", "candidate_std", "delta_mean", "delta_std", "delta_mean_square", "anchor_difference_mean", "anchor_difference_std", "anchor_difference_mean_square", "base_gradient_rms", "candidate_gradient_rms"]
PHASE_FEATURES = [FEATURES.index(k) for k in ["phase", "phase_squared", "spacing_row_mm", "spacing_col_mm", "spacing_plane_mm", "observed_gap_mm", "slice_thickness_mm", "slice_thickness_missing"]]
ENERGY_FEATURES = [FEATURES.index(k) for k in ["phase", "delta_mean_square"]]


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1_048_576), b""):
            h.update(b)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, allow_nan=False, indent=2) + "\n", encoding="utf-8")


def gain_coordinates(errors):
    return np.column_stack([errors[:, 0], errors[:, [0]] - errors[:, 1:5], errors[:, 5], errors[:, [5]] - errors[:, 6:10]])


def as_gains(predictions, coordinates):
    if coordinates == "gain":
        return np.column_stack([np.zeros(len(predictions)), predictions[:, 1:5]]), np.column_stack([np.zeros(len(predictions)), predictions[:, 6:10]])
    return np.column_stack([np.zeros(len(predictions)), predictions[:, [0]] - predictions[:, 1:5]]), np.column_stack([np.zeros(len(predictions)), predictions[:, [5]] - predictions[:, 6:10]])


def visible_features(anchors, base, candidate, support, phase, z_fraction, spacing, thickness, thickness_missing):
    """Pure legal-input feature extraction; no reference, label or identity argument."""
    left, right = anchors
    db, dc = np.gradient(base), np.gradient(candidate)
    gb = np.sqrt(db[0] ** 2 + db[1] ** 2)
    gc = np.sqrt(dc[0] ** 2 + dc[1] ** 2)
    values, keys, counts = [], [], []
    for rr in range(0, base.shape[0], 32):
        for cc in range(0, base.shape[1], 32):
            sl = np.s_[rr:rr + 32, cc:cc + 32]
            mask = support[sl]
            n = int(mask.sum())
            if not n:
                continue
            lv, rv, bv, cv = [v[sl][mask] for v in (left, right, base, candidate)]
            delta, difference = cv - bv, rv - lv
            row = [phase, phase ** 2, z_fraction, (rr + mask.shape[0] / 2) / base.shape[0], (cc + mask.shape[1] / 2) / base.shape[1], base.shape[0] / 256, base.shape[1] / 256,
                   *spacing, spacing[2] * 4, thickness, thickness_missing, n / mask.size]
            row += [float(v.mean()) for v in (lv, rv, bv, cv)]
            row += [float(v.std()) for v in (lv, rv, bv, cv)]
            row += [float(delta.mean()), float(delta.std()), float(np.mean(delta ** 2)), float(difference.mean()), float(difference.std()), float(np.mean(difference ** 2)), float(np.sqrt(np.mean(gb[sl][mask] ** 2))), float(np.sqrt(np.mean(gc[sl][mask] ** 2)))]
            if len(row) != len(FEATURES):
                raise ValueError("Fixed feature count differs")
            values.append(row)
            keys.append((rr, cc))
            counts.append(n)
    return np.asarray(values), np.asarray(keys), np.asarray(counts)


def fit(train_x, train_y, weights, test_x, columns):
    x, tx = train_x[:, columns], test_x[:, columns]
    mu = np.sum(x * weights[:, None], axis=0)
    sd = np.sqrt(np.sum((x - mu) ** 2 * weights[:, None], axis=0))
    sd = np.where(sd < 1e-12, 1., sd)
    design = np.column_stack([np.ones(len(x)), (x - mu) / sd])
    td = np.column_stack([np.ones(len(tx)), (tx - mu) / sd])
    penalty = np.diag([0.] + [RIDGE] * len(columns))
    gram = design.T @ (design * weights[:, None]) + penalty
    beta = np.linalg.solve(gram, design.T @ (train_y * weights[:, None]))
    predictions = td @ beta
    return predictions, {"mean": mu, "std": sd, "beta": beta, "columns": np.asarray(columns)}


def select(support_gains, lesion_gains=None):
    scores = support_gains.copy()
    scores[:, 0] = 0.
    scores[:, 1:] = np.where(scores[:, 1:] > 1e-12, scores[:, 1:], -np.inf)
    if lesion_gains is not None:
        scores[:, 1:] = np.where(lesion_gains[:, 1:] >= 0, scores[:, 1:], -np.inf)
    return GRID[np.argmax(scores, axis=1)]


def metrics(coef, alpha, endpoints):
    losses = [float(np.sum(coef[:, k] - 2 * coef[:, k + 1] * alpha + coef[:, k + 2] * alpha ** 2)) for k in (0, 3, 6)]
    best = min(endpoints[0][0], endpoints[1][0])
    limits = np.minimum(endpoints[0][1:], endpoints[1][1:])
    guards = [losses[j + 1] <= limits[j] for j in range(2)]
    return {"support_target_equal_nmse": losses[0], "lesion_target_equal_nmse": losses[1], "lesion_pixel_weighted_nmse": losses[2], "gain_db_vs_better_fixed": 10 * math.log10(best / losses[0]), "lesion_guard_against_better_fixed": guards,
            "lesion_guard_against_raw": [losses[j + 1] <= endpoints[0][j + 1] for j in range(2)], "strict_development_gate_passed": all(guards) and 10 * math.log10(best / losses[0]) >= .1, "accepted_tiles": int(np.count_nonzero(alpha)), "mean_alpha": float(np.mean(alpha))}


def collect():
    result, proof = read(ORACLE / "attempt_01.json"), read(ORACLE / "independent_pixel_and_dual_verification.json")
    if not result["complete"] or proof["errors"] or proof["result_sha256"] != sha(ORACLE / "attempt_01.json") or proof["run_contract_sha256"] != sha(ORACLE / "run_contract.json"):
        raise ValueError("Fixed-five independent oracle input not current")
    paths = [PLAN, Path(__file__), ORACLE / "attempt_01.json", ORACLE / "run_contract.json", ORACLE / "independent_pixel_and_dual_verification.json", Path(source.__code__.co_filename), ROOT / "experiments/vs_seg_task_cpu_support.py"]
    cases = []
    for p in result["patients"]:
        base = (ROOT / p["source_contract"]).parent
        original, frozen, previous_proof = read(base / "attempt_01.json"), read(base / "run_contract.json"), read(base / "independent_numerical_and_forward_verification.json")
        if previous_proof["errors"] or previous_proof["result_sha256"] != sha(base / "attempt_01.json") or original["run_contract_sha256"] != sha(base / "run_contract.json"):
            raise ValueError("Original developer lineage changed")
        case = next(c for c in frozen["cases"] if c["patient"] == p["patient"])
        saved = next(c for c in original["patients"] if c["patient"] == p["patient"])
        for path, expected in [(ROOT / saved["hat_file"], saved["hat_sha256"]), (ROOT / case["header"]["transfer"]["file"], case["header"]["transfer"]["sha256"]), (ROOT / case["label"]["label_file"], case["label"]["label_sha256"]), (ROOT / p["coefficients_file"], p["coefficients_sha256"])]:
            if sha(path) != expected:
                raise ValueError("Developer input changed")
            paths.append(path)
        paths += [base / name for name in ("attempt_01.json", "run_contract.json", "independent_numerical_and_forward_verification.json")]
        cases.append((case, saved, p))
    if [c[0]["patient"] for c in cases] != ["VS-MC-RC-001", "VS-MC-RC-002", "VS-MC-RC-004", "VS-MC-RC-005", "VS-MC-RC-006"]:
        raise ValueError("Fixed developer roster differs")
    frozen = {"created_utc": datetime.now(timezone.utc).isoformat(), "post_result_development_diagnostic": True, "new_branch_not_original_raw_success": True,
              "features": FEATURES, "phase_features": PHASE_FEATURES, "energy_features": ENERGY_FEATURES, "ridge": RIDGE, "alpha_grid": GRID.tolist(), "roles": [{"patient": c[0]["patient"], "role": "development_LOPO_not_confirmation"} for c in cases],
              "files": [{"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p), "bytes": p.stat().st_size} for p in sorted(set(paths))], "scientific_independent_validation_patients": 0}
    write(OUT / "run_contract.json", frozen)
    return cases


def extract(case, saved, oracle):
    resource_gate()
    native, label = source(case)
    with np.load(ROOT / saved["hat_file"]) as bundle:
        hat = bundle["image_rcz"]
    with np.load(ROOT / oracle["coefficients_file"]) as bundle:
        coef, all_keys = bundle["coefficients"], bundle["tile_z_row_col"]
    observations, targets = saved["observation_indices"], saved["targets"]
    observed = native[:, :, observations]
    lo, span = float(observed.min()), float(observed.max()) - float(observed.min())
    normalized = (observed.astype(float) - lo) / span
    interpolator = PchipInterpolator(observations, observed.astype(float), axis=2)
    summary = case["header"]["summary"]
    thicknesses = summary["slice_thicknesses_mm"]
    thick = float(np.mean(thicknesses)) if thicknesses else 0.
    spacing = summary["native_spacing_rcz_mm"]
    xx, yy, ww, kk, pixel_counts, roi_counts = [], [], [], [], [], []
    max_visible_d_difference = 0.
    pointer = 0
    for z in targets:
        i, phase = z // 4, z % 4 / 4
        raw = ((1 - phase) * observed[:, :, i] + phase * observed[:, :, i + 1]).astype(np.float32) if i == 0 or i + 2 >= len(observations) else interpolator(z).astype(np.float32)
        left, right = observed[:, :, i], observed[:, :, i + 1]
        support = (abs(left) > .01 * max(float(abs(left).max()), 1e-6)) | (abs(right) > .01 * max(float(abs(right).max()), 1e-6))
        roi = support & label[:, :, z]
        b, h = (raw.astype(float) - lo) / span, (hat[:, :, z].astype(float) - lo) / span
        x, keys, counts = visible_features((normalized[:, :, i], normalized[:, :, i + 1]), b, h, support, phase, z / observations[-1], spacing, thick, float(not thicknesses))
        w = counts / (int(support.sum()) * len(targets))
        xx.append(x)
        ww.append(w)
        pixel_counts.extend(counts.tolist())
        for key, n, weight in zip(keys, counts, w):
            rr, cc = map(int, key)
            sl = np.s_[rr:rr + 32, cc:cc + 32]
            e = (native[:, :, z].astype(float)[sl] - raw[sl]) / span
            delta = (hat[:, :, z].astype(float)[sl] - raw[sl]) / span
            sq = np.asarray([(e - a * delta) ** 2 for a in GRID])
            mask, lm = support[sl], roi[sl]
            losses = [float(q[mask].sum()) / n for q in sq] + [float(q[lm].sum()) / n for q in sq]
            yy.append(losses)
            roi_counts.append(int(lm.sum()))
            kk.append((z, rr, cc))
            # Observable energy recomputed from candidates must equal the
            # already independently verified coefficient after normalization.
            visible_d = float(np.mean(delta[mask] ** 2))
            max_visible_d_difference = max(max_visible_d_difference, abs(visible_d * weight - coef[pointer, 2]))
            if not np.allclose(np.asarray(losses[:5]) * weight, coef[pointer, 0] - 2 * coef[pointer, 1] * GRID + coef[pointer, 2] * GRID ** 2, rtol=1e-7, atol=1e-12):
                raise ValueError("Fresh supervision and certified tile endpoint differ")
            pointer += 1
    X, Y, weights, keys = np.concatenate(xx), np.asarray(yy), np.concatenate(ww), np.asarray(kk)
    if len(FEATURES) != 30 or not np.isfinite(X).all() or not np.isfinite(Y).all() or not np.array_equal(keys, all_keys) or not math.isclose(float(weights.sum()), 1., abs_tol=1e-12):
        raise ValueError("Feature/supervision scope gate failed")
    name = case["patient"]
    visible = OUT / (name + "_visible.npz")
    supervised = OUT / (name + "_supervision.npz")
    np.savez_compressed(visible, features=X, tile_z_row_col=keys, weights=weights, support_pixels=np.asarray(pixel_counts), feature_names=np.asarray(FEATURES))
    np.savez_compressed(supervised, absolute_errors=Y, gain_coordinates=gain_coordinates(Y), coefficients=coef, lesion_pixels=np.asarray(roi_counts))
    files = {"visible_file": visible.relative_to(ROOT).as_posix(), "visible_sha256": sha(visible), "supervision_file": supervised.relative_to(ROOT).as_posix(), "supervision_sha256": sha(supervised)}
    print(json.dumps({"extracted": name, "tiles": len(X), "features": X.shape[1], "visible_delta_coefficient_max_difference": max_visible_d_difference}), flush=True)
    return {"patient": name, "X": X, "Y": Y, "weights": weights, "coef": coef, "endpoints": (oracle["baseline_losses"], oracle["candidate_losses"]), "targets": len(targets), "files": files}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    resource = resource_gate()
    OUT.mkdir(exist_ok=False)
    cases = collect()
    data = [extract(*c) for c in cases]
    rows, errors = [], []
    for fold, test in enumerate(data):
        resource_gate()
        training = [p for p in data if p["patient"] != test["patient"]]
        tx = np.concatenate([p["X"] for p in training])
        ty = np.concatenate([p["Y"] for p in training])
        weights = np.concatenate([p["weights"] / 4 for p in training])
        models, predictions = {}, {}
        for name, coordinate, columns in [("full_errors", "error", list(range(30))), ("full_gains", "gain", list(range(30))), ("phase_gains", "gain", PHASE_FEATURES), ("energy_gains", "gain", ENERGY_FEATURES)]:
            pred, model = fit(tx, gain_coordinates(ty) if coordinate == "gain" else ty, weights, test["X"], columns)
            predictions[name] = pred
            models[name] = model
        errors_as_gain = gain_coordinates(predictions["full_errors"])
        equivalence = float(np.max(np.abs(errors_as_gain - predictions["full_gains"])))
        if equivalence > 1e-10:
            errors.append(test["patient"] + " linear-coordinate equivalence failed")
        alphas = {"fixed_0": np.zeros(len(test["X"])), "fixed_0.25": np.full(len(test["X"]), .25), "fixed_0.5": np.full(len(test["X"]), .5), "fixed_0.75": np.full(len(test["X"]), .75), "fixed_1": np.ones(len(test["X"]))}
        summed = np.mean([p["coef"][:, :3].sum(axis=0) for p in training], axis=0)
        common = float(np.clip(summed[1] / summed[2], 0, 1)) if summed[2] else 0.
        alphas["training_common_continuous"] = np.full(len(test["X"]), common)
        for name in ("full_errors", "full_gains", "phase_gains", "energy_gains"):
            sg, lg = as_gains(predictions[name], "error" if name == "full_errors" else "gain")
            alphas[name + "_support"] = select(sg)
            if name.startswith("full"):
                alphas[name + "_joint"] = select(sg, lg)
        for endpoint in ("support", "joint"):
            if not np.array_equal(alphas["full_errors_" + endpoint], alphas["full_gains_" + endpoint]):
                errors.append(test["patient"] + " equivalent coordinate decisions differ: " + endpoint)
        accepted = alphas["full_gains_joint"][alphas["full_gains_joint"] != 0]
        random = np.zeros(len(test["X"]))
        rng = np.random.default_rng(20261002 + fold)
        positions = rng.choice(len(random), len(accepted), replace=False)
        random[positions] = rng.permutation(accepted)
        alphas["random_matched_joint"] = random
        policy_file, model_file = OUT / (test["patient"] + "_predictions_and_policies.npz"), OUT / (test["patient"] + "_fitted_models.npz")
        np.savez_compressed(policy_file, **{"prediction_" + k: v for k, v in predictions.items()}, **{"alpha_" + k: v for k, v in alphas.items()})
        np.savez_compressed(model_file, **{model_name + "_" + key: value for model_name, model in models.items() for key, value in model.items()})
        row = {"patient": test["patient"], "training_patients": [p["patient"] for p in training], "development_only": True, "tiles": len(test["X"]), "targets": test["targets"], **test["files"],
               "model_file": model_file.relative_to(ROOT).as_posix(), "model_sha256": sha(model_file), "policies_file": policy_file.relative_to(ROOT).as_posix(), "policies_sha256": sha(policy_file),
               "training_common_alpha": common, "maximum_linear_coordinate_prediction_difference": equivalence, "policies": {k: metrics(test["coef"], a, test["endpoints"]) for k, a in alphas.items()}}
        rows.append(row)
        print(json.dumps({"patient": test["patient"], "linear_equivalence_max_difference": equivalence, "joint": row["policies"]["full_gains_joint"], "support": row["policies"]["full_gains_support"], "common": row["policies"]["training_common_continuous"]}), flush=True)
    means = {name: float(np.mean([r["policies"][name]["support_target_equal_nmse"] for r in rows])) for name in rows[0]["policies"]}
    controls = ["training_common_continuous", "phase_gains_support", "energy_gains_support", "random_matched_joint"]
    all_patient_guards = all(r["policies"]["full_gains_joint"]["strict_development_gate_passed"] for r in rows)
    beats_controls = all(means["full_gains_joint"] < means[k] for k in controls)
    output = {"created_utc": datetime.now(timezone.utc).isoformat(), "complete": len(rows) == 5 and not errors, "run_contract_sha256": sha(OUT / "run_contract.json"), "resource_gate": resource,
              "patients": rows, "errors": errors, "patient_equal_mean_support_nmse": means, "all_five_joint_patient_gates_passed": all_patient_guards, "joint_beats_all_fixed_controls_on_mean_nmse": beats_controls,
              "fixed_visible_joint_diagnostic_gate_passed": all_patient_guards and beats_controls and not errors, "post_result_development_diagnostic": True, "original_raw_development_gate_passed": False,
              "gpu_used": False, "neural_networks_executed": 0, "task_fidelity_evaluated": False, "scientific_independent_validation_patients": 0, "publication_claim_confirmed": False}
    write(OUT / "attempt_01.json", output)
    print(json.dumps({k: output[k] for k in ("complete", "errors", "all_five_joint_patient_gates_passed", "joint_beats_all_fixed_controls_on_mean_nmse", "fixed_visible_joint_diagnostic_gate_passed")}), flush=True)
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
