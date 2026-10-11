"""Independent augmented least-squares refit and all-policy actual-pixel audit."""
from __future__ import annotations
import ast
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
from vs_seg_task_cpu_support import ROOT, resource_gate
from verify_mc_rc_five_developer_constrained_oracle import source

OUT = ROOT / "experiments/mc_rc_visible_joint_development_diagnostic"
GRID = np.array([0., .25, .5, .75, 1.])

def read(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))

def sha(p):
    h = hashlib.sha256()
    with Path(p).open("rb") as stream:
        for block in iter(lambda: stream.read(1_048_576), b""):
            h.update(block)
    return h.hexdigest()

def transform_errors(y):
    out = np.empty_like(y)
    out[:, 0], out[:, 5] = y[:, 0], y[:, 5]
    for j in range(1, 5):
        out[:, j] = y[:, 0] - y[:, j]
        out[:, j + 5] = y[:, 5] - y[:, j + 5]
    return out

def independently_fit(x, y, w, test, columns, ridge):
    x, test = x[:, columns], test[:, columns]
    mean = np.average(x, weights=w, axis=0)
    scale = np.sqrt(np.average((x - mean) ** 2, weights=w, axis=0))
    scale[scale < 1e-12] = 1.
    design = np.column_stack([np.ones(len(x)), (x - mean) / scale])
    test_design = np.column_stack([np.ones(len(test)), (test - mean) / scale])
    penalty = np.diag([0.] + [math.sqrt(ridge)] * len(columns))
    augmented_x = np.vstack([np.sqrt(w)[:, None] * design, penalty])
    augmented_y = np.vstack([np.sqrt(w)[:, None] * y, np.zeros((len(columns) + 1, y.shape[1]))])
    beta = np.linalg.lstsq(augmented_x, augmented_y, rcond=None)[0]
    return test_design @ beta, mean, scale, beta

def choose(pred, is_error, joint):
    scores = np.zeros((len(pred), 5))
    scores[:, 1:] = pred[:, [0]] - pred[:, 1:5] if is_error else pred[:, 1:5]
    lesion = pred[:, [5]] - pred[:, 6:10] if is_error else pred[:, 6:10]
    eligible = scores[:, 1:] > 1e-12
    if joint:
        eligible &= lesion >= 0
    scores[:, 1:][~eligible] = -np.inf
    return GRID[np.argmax(scores, axis=1)]

def independent_raw_pchip(anchors, i, t):
    if i < 1 or i + 2 >= len(anchors):
        return ((1 - t) * anchors[i] + t * anchors[i + 1]).astype(np.float32)
    before, left, right, after = [np.asarray(anchors[j], dtype=float) for j in (i - 1, i, i + 1, i + 2)]
    slopes = []
    for a, b in ((left - before, right - left), (right - left, after - right)):
        out = np.zeros_like(a)
        mask = (a > 0) & (b > 0) | (a < 0) & (b < 0)
        out[mask] = 2 / (1 / a[mask] + 1 / b[mask])
        slopes.append(out)
    return ((2*t**3 - 3*t**2 + 1)*left + (t**3 - 2*t**2 + t)*slopes[0] + (-2*t**3 + 3*t**2)*right + (t**3 - t**2)*slopes[1]).astype(np.float32)

def independent_feature_row(left, right, base, candidate, support, rr, cc, phase, z_fraction, spacing, thickness, missing):
    sl = np.s_[rr:rr + 32, cc:cc + 32]
    mask = support[sl]
    ls, rs, bs, cs = [v[sl][mask] for v in (left, right, base, candidate)]
    row = [phase, phase*phase, z_fraction, (rr + mask.shape[0]/2)/base.shape[0], (cc + mask.shape[1]/2)/base.shape[1], base.shape[0]/256, base.shape[1]/256, *spacing, 4*spacing[2], thickness, missing, int(mask.sum())/mask.size]
    row.extend(float(np.average(v)) for v in (ls, rs, bs, cs))
    row.extend(float(np.std(v, ddof=0)) for v in (ls, rs, bs, cs))
    for v in (cs - bs, rs - ls):
        row.extend([float(np.average(v)), float(np.std(v)), float(np.dot(v, v) / len(v))])
    for image in (base, candidate):
        gr, gc = np.gradient(image)
        row.append(float(np.sqrt(np.mean((gr[sl][mask] ** 2 + gc[sl][mask] ** 2)))))
    return np.asarray(row)

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    resource_gate()
    result, contract = read(OUT / "attempt_01.json"), read(OUT / "run_contract.json")
    errors, checked = [], []
    def require(ok, message):
        if not ok:
            errors.append(message)
    def close(a, b, message, atol=1e-10):
        require(np.allclose(a, b, rtol=1e-7, atol=atol), message)
    require(result["complete"] and not result["errors"] and len(result["patients"]) == 5, "Incomplete fixed-five producer output")
    require(sha(OUT / "run_contract.json") == result["run_contract_sha256"], "Run contract changed")
    for entry in contract["files"]:
        p = (ROOT / entry["path"]).resolve()
        require(p.is_relative_to(ROOT) and p.is_file() and sha(p) == entry["sha256"], "Frozen input changed " + entry["path"])
    tree = ast.parse((ROOT / "experiments/mc_rc_visible_joint_development_diagnostic.py").read_text(encoding="utf-8"))
    feature_function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "visible_features")
    require([a.arg for a in feature_function.args.args] == ["anchors", "base", "candidate", "support", "phase", "z_fraction", "spacing", "thickness", "thickness_missing"], "Visible feature input signature changed")
    forbidden = {"native", "label", "reference", "oracle", "coef", "patient", "open", "read", "source", "load", "eval", "exec"}
    referenced = {n.id for n in ast.walk(feature_function) if isinstance(n, ast.Name)}
    require(not referenced & forbidden, "Hidden inputs / I/O in feature function")
    all_data = []
    for p in result["patients"]:
        for stem in ("visible", "supervision", "model", "policies"):
            require(sha(ROOT / p[stem + "_file"]) == p[stem + "_sha256"], "Saved data changed " + stem)
        with np.load(ROOT / p["visible_file"]) as pack:
            require(set(pack.files) == {"features", "tile_z_row_col", "weights", "support_pixels", "feature_names"}, "Visible package contains undeclared fields")
            X, keys, weights, counts = [pack[k] for k in ("features", "tile_z_row_col", "weights", "support_pixels")]
            require(pack["feature_names"].tolist() == contract["features"], "Feature names changed")
        with np.load(ROOT / p["supervision_file"]) as pack:
            Y, gains, lesion_counts = pack["absolute_errors"], pack["gain_coordinates"], pack["lesion_pixels"]
        close(gains, transform_errors(Y), "Supervised gain transform differs")
        require(math.isclose(float(weights.sum()), 1., abs_tol=1e-12) and X.shape[1] == 30, "Weight/feature scope differs")
        all_data.append({"row": p, "X": X, "Y": Y, "weights": weights, "keys": keys, "counts": counts, "lesion_counts": lesion_counts})
    total_targets = total_tiles = sampled_features = 0
    for fold, test in enumerate(all_data):
        resource_gate()
        p, name = test["row"], test["row"]["patient"]
        before_errors = len(errors)
        training = [d for d in all_data if d["row"]["patient"] != name]
        require(p["training_patients"] == [d["row"]["patient"] for d in training] and name not in p["training_patients"], "LOPO patient split changed")
        x, y, w = np.concatenate([d["X"] for d in training]), np.concatenate([d["Y"] for d in training]), np.concatenate([d["weights"] / 4 for d in training])
        with np.load(ROOT / p["policies_file"]) as pack:
            stored = {k: pack[k] for k in pack.files}
        with np.load(ROOT / p["model_file"]) as pack:
            models = {k: pack[k] for k in pack.files}
        refitted, max_prediction_difference = {}, 0.
        for model_name, is_error, columns in [("full_errors", True, list(range(30))), ("full_gains", False, list(range(30))), ("phase_gains", False, contract["phase_features"]), ("energy_gains", False, contract["energy_features"])]:
            pred, mean, scale, beta = independently_fit(x, y if is_error else transform_errors(y), w, test["X"], columns, contract["ridge"])
            refitted[model_name] = pred
            diff = float(np.max(abs(pred - stored["prediction_" + model_name])))
            max_prediction_difference = max(max_prediction_difference, diff)
            require(diff <= 1e-10, "Independent ridge prediction differs " + name + model_name)
            for suffix, value in (("mean", mean), ("std", scale), ("beta", beta), ("columns", columns)):
                close(value, models[model_name + "_" + suffix], "Independent fitted parameters differ " + name + model_name + suffix)
            for joint in ([False, True] if model_name.startswith("full") else [False]):
                policy_name = model_name + ("_joint" if joint else "_support")
                require(np.array_equal(choose(pred, is_error, joint), stored["alpha_" + policy_name]), "Independent policy differs " + name + policy_name)
        require(np.max(abs(transform_errors(refitted["full_errors"]) - refitted["full_gains"])) <= 1e-10, "Linear label-coordinate equivalence not reproduced")
        accepted = stored["alpha_full_gains_joint"][stored["alpha_full_gains_joint"] != 0]
        rng = np.random.default_rng(20261002 + fold)
        random = np.zeros(len(test["X"]))
        positions = rng.choice(len(random), len(accepted), replace=False)
        assigned = rng.permutation(accepted)
        random[positions] = assigned
        require(np.array_equal(random, stored["alpha_random_matched_joint"]), "Matched random control differs")
        # Check the training-only shared alpha using its separate supervision.
        sums = []
        for d in training:
            with np.load(ROOT / d["row"]["supervision_file"]) as pack:
                sums.append(pack["coefficients"][:, :3].sum(axis=0))
        aggregate = np.mean(sums, axis=0)
        common = min(1., max(0., float(aggregate[1] / aggregate[2]))) if aggregate[2] else 0.
        close(common, p["training_common_alpha"], "Training-only common alpha differs", atol=1e-12)
        require(np.array_equal(stored["alpha_training_common_continuous"], np.full(len(test["X"]), common)), "Common-alpha policy differs")
        oracle_result = read(ROOT / "experiments/mc_rc_five_developer_constrained_oracle/attempt_01.json")
        prior = next(c for c in oracle_result["patients"] if c["patient"] == name)
        prior_contract = read(ROOT / prior["source_contract"])
        case = next(c for c in prior_contract["cases"] if c["patient"] == name)
        prior_raw = read((ROOT / prior["source_contract"]).parent / "attempt_01.json")
        saved = next(c for c in prior_raw["patients"] if c["patient"] == name)
        native, label = source(case)
        with np.load(ROOT / saved["hat_file"]) as pack:
            hat = pack["image_rcz"]
        anchors = [native[:, :, z] for z in saved["observation_indices"]]
        lo = min(float(a.min()) for a in anchors)
        span = max(float(a.max()) for a in anchors) - lo
        policy_names = list(p["policies"])
        require(set(stored) == {"prediction_" + k for k in refitted} | {"alpha_" + k for k in policy_names}, "Policy/prediction inventory differs")
        roi_indices = np.flatnonzero(test["lesion_counts"] > 0)
        sample = sorted(set([0, len(test["X"]) // 2, len(test["X"]) - 1] + (roi_indices[[0, -1]].tolist() if len(roi_indices) else [])))
        plane_scores = {k: [] for k in policy_names}
        maximum_sample_feature_difference = 0.
        for z in saved["targets"]:
            i, phase = z // 4, z % 4 / 4
            raw = independent_raw_pchip(anchors, i, phase)
            left, right = anchors[i], anchors[i + 1]
            support = (abs(left) > .01 * max(float(abs(left).max()), 1e-6)) | (abs(right) > .01 * max(float(abs(right).max()), 1e-6))
            roi = support & label[:, :, z]
            e = (native[:, :, z].astype(float) - raw) / span
            delta = (hat[:, :, z].astype(float) - raw) / span
            indices = np.flatnonzero(test["keys"][:, 0] == z)
            for index in indices:
                _, rr, cc = test["keys"][index]
                mask = support[rr:rr + 32, cc:cc + 32]
                lm = roi[rr:rr + 32, cc:cc + 32]
                require(int(mask.sum()) == test["counts"][index], "Observable tile support count differs")
                require(int(lm.sum()) == test["lesion_counts"][index], "Supervised lesion tile count differs")
                ev, dv = e[rr:rr + 32, cc:cc + 32], delta[rr:rr + 32, cc:cc + 32]
                squares = [(ev - a * dv) ** 2 for a in GRID]
                actual_targets = [float(sq[mask].sum()) / int(mask.sum()) for sq in squares] + [float(sq[lm].sum()) / int(mask.sum()) for sq in squares]
                close(actual_targets, test["Y"][index], "All-tile actual supervised targets differ " + name, atol=1e-10)
                close(test["weights"][index], int(mask.sum()) / (int(support.sum()) * len(saved["targets"])), "Observable patient/target weight differs", atol=1e-14)
                if index in sample:
                    summary = case["header"]["summary"]
                    thick = float(np.mean(summary["slice_thicknesses_mm"])) if summary["slice_thicknesses_mm"] else 0.
                    feature = independent_feature_row((left.astype(float) - lo) / span, (right.astype(float) - lo) / span, (raw.astype(float) - lo) / span, (hat[:, :, z].astype(float) - lo) / span, support, int(rr), int(cc), phase, z / saved["observation_indices"][-1], summary["native_spacing_rcz_mm"], thick, float(not summary["slice_thicknesses_mm"]))
                    difference = float(np.max(abs(feature - test["X"][index])))
                    maximum_sample_feature_difference = max(maximum_sample_feature_difference, difference)
                    close(feature, test["X"][index], "Sampled native visible features differ " + name, atol=1e-10)
                    sampled_features += 1
            for policy in policy_names:
                amap = np.zeros(raw.shape)
                for index in indices:
                    _, rr, cc = test["keys"][index]
                    amap[rr:rr + 32, cc:cc + 32] = stored["alpha_" + policy][index]
                sq = (e - amap * delta) ** 2
                plane_scores[policy].append([int(support.sum()), float(sq[support].sum()), int(roi.sum()), float(sq[roi].sum())])
        actual = {}
        for policy, rows in plane_scores.items():
            lesion = [r for r in rows if r[2] > 0]
            actual[policy] = [float(np.mean([r[1] / r[0] for r in rows])), float(np.mean([r[3] / r[2] for r in lesion])), sum(r[3] for r in lesion) / sum(r[2] for r in lesion)]
        baseline, candidate = np.asarray(actual["fixed_0"]), np.asarray(actual["fixed_1"])
        guards = {}
        for policy in policy_names:
            values, old = actual[policy], p["policies"][policy]
            close(values, [old["support_target_equal_nmse"], old["lesion_target_equal_nmse"], old["lesion_pixel_weighted_nmse"]], "Actual pixel metrics differ " + name + policy)
            gain = 10 * math.log10(min(baseline[0], candidate[0]) / values[0])
            close(gain, old["gain_db_vs_better_fixed"], "Actual pixel gain differs " + name + policy, atol=1e-9)
            guard = (np.asarray(values[1:]) <= np.minimum(baseline[1:], candidate[1:])).tolist()
            raw_guard = (np.asarray(values[1:]) <= baseline[1:]).tolist()
            require(guard == old["lesion_guard_against_better_fixed"] and raw_guard == old["lesion_guard_against_raw"], "Actual strict lesion guard differs " + name + policy)
            require((all(guard) and gain >= .1) == old["strict_development_gate_passed"], "Actual patient gate differs")
            guards[policy] = all(guard) and gain >= .1
        checked.append({"patient": name, "training_patients": p["training_patients"], "targets": len(saved["targets"]), "tiles": len(test["X"]), "policies": len(policy_names), "independent_ridge_prediction_max_difference": max_prediction_difference, "sampled_feature_rows": len(sample), "sampled_feature_max_difference": maximum_sample_feature_difference, "actual_pixel_losses_by_policy": actual, "patient_strict_gates": guards, "errors": errors[before_errors:], "independent_confirmation": False})
        total_targets += len(saved["targets"])
        total_tiles += len(test["X"])
        print(json.dumps({"patient": name, "targets": len(saved["targets"]), "policies": len(policy_names), "errors": errors[before_errors:], "refit_max_difference": max_prediction_difference}), flush=True)
        del native, label, hat, anchors
    actual_means = {k: float(np.mean([p["actual_pixel_losses_by_policy"][k][0] for p in checked])) for k in checked[0]["actual_pixel_losses_by_policy"]}
    close(list(actual_means.values()), list(result["patient_equal_mean_support_nmse"].values()), "Patient-equal support summary differs")
    passed = all(p["patient_strict_gates"]["full_gains_joint"] for p in checked)
    controls = ["training_common_continuous", "phase_gains_support", "energy_gains_support", "random_matched_joint"]
    beats = all(actual_means["full_gains_joint"] < actual_means[k] for k in controls)
    require(passed == result["all_five_joint_patient_gates_passed"] and beats == result["joint_beats_all_fixed_controls_on_mean_nmse"] and (passed and beats) == result["fixed_visible_joint_diagnostic_gate_passed"], "Diagnostic conclusion differs")
    require(total_targets == 240 and total_tiles == 34872 and not result["original_raw_development_gate_passed"] and result["scientific_independent_validation_patients"] == 0 and not result["publication_claim_confirmed"], "Scientific scope changed")
    proof = {"created_utc": datetime.now(timezone.utc).isoformat(), "verification_script_sha256": sha(__file__), "result_sha256": sha(OUT / "attempt_01.json"), "run_contract_sha256": sha(OUT / "run_contract.json"), "scope": "All folds refit by augmented lstsq; all supervision tiles and all policies/targets freshly scored on actual pixels using independent Hermite; 25 sampled native feature rows, all tile support/lesion counts and weights, visible function/package dependency audit", "decoder": "fresh decode via previously certified source helper; no new decoder-independence claim", "patients": checked, "targets": total_targets, "tiles": total_tiles, "supervised_scalar_targets_independently_recomputed": total_tiles * 10, "sampled_native_feature_rows": sampled_features, "errors": errors, "fixed_visible_joint_diagnostic_gate_passed": passed and beats, "gpu_used": False, "neural_networks_executed": 0, "scientific_independent_validation_patients": 0, "publication_claim_confirmed": False}
    (OUT / "independent_refit_and_pixel_verification.json").write_text(json.dumps(proof, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: proof[k] for k in ("targets", "tiles", "sampled_native_feature_rows", "errors", "fixed_visible_joint_diagnostic_gate_passed")}), flush=True)
    return int(bool(errors))

if __name__ == "__main__":
    raise SystemExit(main())
