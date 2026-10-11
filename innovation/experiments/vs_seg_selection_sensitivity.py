"""CPU-only secondary selection analysis; require the entire verified frozen cohort."""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/vs_seg_selection_sensitivity"
COHORT = ROOT / "experiments/vs_seg_full_volume_cohort"
QUEUE = ROOT / "experiments/vs_seg_full_volume_queue"
COVERAGE = ROOT / "experiments/vs_seg_full_volume_coverage"
PLAN = ROOT / "VS_SEG_SELECTION_SENSITIVITY_PREPARATION_2026-10-02.md"
EXPECTED_CONTRACT = "061d9f0912197321a62cbc0871195b34ecca7a3d20c9efa263bb19d0a729c7d5"
CONDITIONS = ("native", "raw_linear", "raw_pchip", "pipeline_linear", "pipeline_pchip", "hat", "swinir")
MODELS = ("hat", "swinir")
BASELINES = ("raw_linear", "raw_pchip", "pipeline_linear", "pipeline_pchip")
LABELS = ("original_json", "rtstruct")
SEED, DRAWS = 20261021, 5000


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, allow_nan=False, indent=2) + "\n", encoding="utf-8")


def completion_gate():
    """Return before opening patient effect records if the whole queue is incomplete."""
    contract = read(COHORT / "run_contract.json")
    if sha(COHORT / "run_contract.json") != EXPECTED_CONTRACT:
        raise ValueError("Frozen contract digest changed")
    if len(contract["main_roster"]) != 45 or len(set(contract["main_roster"])) != 45 or set(contract["conditions"]) != set(CONDITIONS):
        raise ValueError("Frozen roster or conditions changed")
    paths = sorted(QUEUE.glob("attempt_*.json"))
    if not paths:
        return {"allowed": False, "reason": "Fixed full queue has not started", "patient_effects_read": False}, contract
    state = read(paths[-1])
    if not state.get("complete") or state.get("active_stage") != "complete":
        return {"allowed": False, "reason": "Fixed full queue inference and independent verification are incomplete",
                "queue_stage": state.get("active_stage"), "queue_attempt_file": paths[-1].relative_to(ROOT).as_posix(),
                "patient_effects_read": False, "formal_or_secondary_statistics_computed": False}, contract
    if state["contract_sha256"] != EXPECTED_CONTRACT:
        raise ValueError("Completed queue contract differs")
    final = read(QUEUE / "completed_analysis.json")
    if final["contract_sha256"] != EXPECTED_CONTRACT or final["main_patients"] != 45 or not final["independent_saved_outputs_verified"]:
        raise ValueError("Completed report does not certify all main patients")
    coverage, proof = read(COVERAGE / "attempt_01.json"), read(COVERAGE / "independent_verification.json")
    roster = contract["main_roster"]
    if not coverage["complete"] or coverage["errors"] or coverage["contract_sha256"] != EXPECTED_CONTRACT or coverage["fixed_main_roster"] != roster:
        raise ValueError("Actual support coverage is incomplete or has a different roster")
    if not proof["complete"] or proof["errors"] or proof["contract_sha256"] != EXPECTED_CONTRACT or proof["source_result_sha256"] != sha(COVERAGE / "attempt_01.json") or proof["checked_patients"] != roster:
        raise ValueError("Independent coverage proof differs")
    hashes = {p: sha(p) for p in (ROOT / "experiments/vs_seg_full_volume_coverage.py", ROOT / "experiments/verify_vs_seg_full_volume_coverage.py",
                                   ROOT / "experiments/verify_vs_seg_full_volume_cohort.py")}
    if coverage["script_sha256"] != hashes[ROOT / "experiments/vs_seg_full_volume_coverage.py"] or proof["script_sha256"] != hashes[ROOT / "experiments/verify_vs_seg_full_volume_coverage.py"]:
        raise ValueError("Coverage implementation does not match its evidence")
    verifier_sha = hashes[ROOT / "experiments/verify_vs_seg_full_volume_cohort.py"]
    for patient in roster:
        proof = read(COHORT / f"verification_{patient}.json")
        if proof["errors"] or proof["contract_sha256"] != EXPECTED_CONTRACT or proof["script_sha256"] != verifier_sha or not proof["reconstruction_pixels_independently_regenerated"]:
            raise ValueError("Patient output has no valid independent regeneration: " + patient)
        if {(r["patient"], r["condition"]) for r in proof["checked_conditions"]} != {(patient, name) for name in CONDITIONS} or len(proof["checked_conditions"]) != 7:
            raise ValueError("Patient proof is not a complete seven-condition set: " + patient)
    return {"allowed": True, "queue_attempt_file": paths[-1].relative_to(ROOT).as_posix(),
            "completed_analysis_sha256": sha(QUEUE / "completed_analysis.json"),
            "coverage_sha256": sha(COVERAGE / "attempt_01.json"), "coverage_proof_sha256": sha(COVERAGE / "independent_verification.json"),
            "all_main_patients_independently_regenerated": True}, contract


def load_verified_records(roster, coverage):
    records, provenance = {}, []
    for patient in roster:
        by_condition = {}
        for path in sorted((COHORT / "patients" / patient).glob("*_attempt_*.json")):
            record = read(path)
            if not record.get("complete"):
                continue
            name = record["condition"]
            if record["contract_sha256"] != EXPECTED_CONTRACT or record["patient"] != patient or name in by_condition or name not in CONDITIONS:
                raise ValueError("Patient condition contract, identity, or uniqueness differs")
            pred = ROOT / record["prediction_file"]
            if sha(pred) != record["prediction_sha256"] or record["reference_masks_sha256"] != coverage[patient]["reference_masks_sha256"]:
                raise ValueError("Patient saved prediction or coverage mask differs")
            by_condition[name] = record
            provenance.append({"file": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "prediction_sha256": sha(pred)})
        if set(by_condition) != set(CONDITIONS):
            raise ValueError("Patient conditions missing: " + patient)
        proof = read(COHORT / f"verification_{patient}.json")
        if {(r["condition"], r["prediction_sha256"]) for r in proof["checked_conditions"]} != {(name, rec["prediction_sha256"]) for name, rec in by_condition.items()}:
            raise ValueError("Patient proof does not match saved records")
        records[patient] = by_condition
    return records, provenance


def nullable_number(value):
    if value is None:
        return np.nan
    value = float(value)
    if not math.isfinite(value):
        raise ValueError("Nonfinite endpoint must be explicitly null")
    return value


def selected_image(record, region, weighting, indices):
    rows = {r["z"]: r[region] for r in record["per_plane_image_errors"]}
    if len(indices) != 4 or len(set(indices)) != 4 or any(z not in rows for z in indices):
        raise ValueError("Old selected targets are not four distinct internal targets")
    if weighting == "target_equal_nmse":
        vals = [rows[z]["nmse"] for z in indices if rows[z]["pixels"] > 0]
        if any(v is None for v in vals):
            raise ValueError("Positive pixel count with undefined NMSE")
        return float(np.mean(vals)) if vals else None
    pixels = sum(rows[z]["pixels"] for z in indices)
    return sum(rows[z]["sse"] for z in indices) / pixels if pixels else None


def sample_means(values, group, draws):
    good = np.isfinite(values) & group
    point = float(np.mean(values[good])) if good.any() else None
    sampled_good = good[draws]
    counts = sampled_good.sum(axis=1)
    totals = np.where(sampled_good, np.nan_to_num(values)[draws], 0.0).sum(axis=1)
    estimates = np.full(len(draws), np.nan)
    np.divide(totals, counts, out=estimates, where=counts > 0)
    return point, estimates, int(good.sum())


def interval(point, sampled):
    valid = sampled[np.isfinite(sampled)]
    return {"mean_difference": point, "ci95_percentile": [float(x) for x in np.percentile(valid, [2.5, 97.5])] if len(valid) else None,
            "valid_bootstrap_draws": len(valid), "undefined_bootstrap_draws": len(sampled) - len(valid)}


def summarise(full_values, eligible, draws, four_values=None):
    full = np.array([nullable_number(v) for v in full_values], dtype=float)
    eligible = np.asarray(eligible, dtype=bool)
    if full.shape != eligible.shape or draws.ndim != 2 or draws.shape[1] != len(full) or np.any(draws < 0) or np.any(draws >= len(full)):
        raise ValueError("Paired patient array or bootstrap draw shape differs")
    groups = {"all": np.ones(len(full), dtype=bool), "eligible": eligible, "excluded": ~eligible}
    points, samples, result = {}, {}, {"group_counts": {}, "estimates": {}}
    for key, mask in groups.items():
        point, sampled, count = sample_means(full, mask, draws)
        points[key], samples[key] = point, sampled
        result["group_counts"][key] = {"planned_patients": int(mask.sum()), "finite_patients": count, "undefined_patients": int(mask.sum()) - count}
        result["estimates"][key] = interval(point, sampled)
    if four_values is not None:
        four = np.array([nullable_number(v) for v in four_values], dtype=float)
        if four.shape != full.shape or np.any(np.isfinite(four) & ~eligible):
            raise ValueError("Four-target values supplied outside eligible patient group")
        point, sampled, count = sample_means(four, eligible, draws)
        points["four_targets"], samples["four_targets"] = point, sampled
        result["group_counts"]["four_targets"] = {"planned_patients": int(eligible.sum()), "finite_patients": count, "undefined_patients": int(eligible.sum()) - count}
        result["estimates"]["four_targets"] = interval(point, sampled)
    differences = {"patient_selection_shift": ("eligible", "all"), "eligible_minus_excluded": ("eligible", "excluded")}
    if four_values is not None:
        differences.update(target_selection_shift=("four_targets", "eligible"), total_four_target_shift=("four_targets", "all"))
    for key, (left, right) in differences.items():
        point = points[left] - points[right] if points[left] is not None and points[right] is not None else None
        result["estimates"][key] = interval(point, samples[left] - samples[right])
    all_count = result["group_counts"]["all"]["finite_patients"]
    fraction = result["group_counts"]["eligible"]["finite_patients"] / all_count if all_count else None
    residual = None
    if all(points[k] is not None for k in ("all", "eligible", "excluded")):
        residual = points["all"] - fraction * points["eligible"] - (1 - fraction) * points["excluded"]
        if abs(residual) > 1e-10:
            raise ValueError("Finite-patient weighted composition identity failed")
    result["composition_identity"] = {"eligible_fraction_of_finite_all": fraction, "residual": residual, "is_causal_decomposition": False}
    result["point_estimate_sign_changes"] = {"eligible_vs_all": points["all"] is not None and points["eligible"] is not None and points["all"] * points["eligible"] < 0}
    if four_values is not None:
        result["point_estimate_sign_changes"]["four_targets_vs_all"] = points["all"] is not None and points["four_targets"] is not None and points["all"] * points["four_targets"] < 0
        result["point_estimate_sign_changes"]["four_targets_vs_eligible"] = points["eligible"] is not None and points["four_targets"] is not None and points["eligible"] * points["four_targets"] < 0
        if all(points[k] is not None for k in ("all", "eligible", "four_targets")):
            result["shift_identity_residual"] = (points["four_targets"] - points["all"]) - ((points["eligible"] - points["all"]) + (points["four_targets"] - points["eligible"]))
    return result


def difference(left, right):
    return left - right if left is not None and right is not None else None


def analyse(records, coverage, roster):
    if len(roster) != 45 or set(records) != set(roster) or set(coverage) != set(roster):
        raise ValueError("Analysis requires exactly the fixed 45 main patients")
    draws = np.random.default_rng(SEED).integers(0, 45, size=(DRAWS, 45))
    endpoints = []
    for label in LABELS:
        eligible = [coverage[p]["labels"][label]["old_target_rule_eligible"] for p in roster]
        for model in MODELS:
            for baseline in BASELINES:
                for region in ("support", label + "_lesion"):
                    for weighting in ("target_equal_nmse", "pixel_weighted_nmse"):
                        values, four = [], []
                        for p, ok in zip(roster, eligible):
                            pair = (records[p][model], records[p][baseline])
                            values.append(difference(*(r["image_metrics"][region][weighting] for r in pair)))
                            indices = coverage[p]["labels"][label]["selected_four_indices"]
                            four.append(difference(*(selected_image(r, region, weighting, indices) for r in pair)) if ok else None)
                        endpoints.append({"label_and_qualification": label, "model": model, "baseline": baseline, "endpoint": region + "/" + weighting,
                                          "kind": "image", **summarise(values, eligible, draws, four)})
                for domain, metric in (("full", "dice"), ("observed_anchor_slab", "dice"), ("full", "absolute_relative_volume_error")):
                    values = [difference(*(records[p][name]["task_metrics"][label][domain][metric] for name in (model, baseline))) for p in roster]
                    endpoints.append({"label_and_qualification": label, "model": model, "baseline": baseline, "endpoint": domain + "/" + metric,
                                      "kind": "task", **summarise(values, eligible, draws)})
    return {"endpoints": endpoints, "bootstrap_seed": SEED, "bootstrap_draws": DRAWS,
            "patient_resamples_shared_across_all_endpoints": True, "multiple_comparison_control": "None; descriptive secondary intervals only",
            "primary_claim_changed": False, "publication_claim_confirmed": False}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    attempt = len(list(OUT.glob("attempt_*.json"))) + 1
    gate, contract = completion_gate()
    result = {"attempt": attempt, "created_utc": datetime.now(timezone.utc).isoformat(), "contract_sha256": EXPECTED_CONTRACT,
              "script_sha256": sha(Path(__file__)), "plan_sha256": sha(PLAN), "gate": gate,
              "complete": False, "post_first_patient_secondary_exploration": True, "gpu_used": False}
    if gate["allowed"]:
        coverage = {r["patient"]: r for r in read(COVERAGE / "attempt_01.json")["patients"]}
        records, provenance = load_verified_records(contract["main_roster"], coverage)
        result.update(analysis=analyse(records, coverage, contract["main_roster"]), record_provenance=provenance, complete=True)
    write(OUT / f"attempt_{attempt:02d}.json", result)
    print(json.dumps({"complete": result["complete"], "gate": gate, "gpu_used": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
