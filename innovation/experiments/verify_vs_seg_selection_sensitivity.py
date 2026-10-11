"""Known-answer checks and a separate scalar bootstrap; no patient effect records."""
from __future__ import annotations

import math
import statistics
from pathlib import Path

import numpy as np

from vs_seg_selection_sensitivity import OUT, analyse, selected_image, sha, summarise, write


def percentile_scalar(values, percent):
    ordered = sorted(values)
    position = (len(ordered) - 1) * percent / 100
    lower, upper = math.floor(position), math.ceil(position)
    return ordered[lower] + (position - lower) * (ordered[upper] - ordered[lower])


def scalar_mean(values):
    finite = [v for v in values if v is not None]
    return statistics.mean(finite) if finite else None


def scalar_bootstrap(values, eligibility, four, draws):
    distributions = {k: [] for k in ("all", "eligible", "excluded", "four_targets", "patient_selection_shift", "eligible_minus_excluded",
                                     "target_selection_shift", "total_four_target_shift")}
    for draw in draws:
        a = scalar_mean([values[i] for i in draw])
        b = scalar_mean([values[i] for i in draw if eligibility[i]])
        e = scalar_mean([values[i] for i in draw if not eligibility[i]])
        c = scalar_mean([four[i] for i in draw if eligibility[i]])
        row = {"all": a, "eligible": b, "excluded": e, "four_targets": c}
        for key, left, right in (("patient_selection_shift", b, a), ("eligible_minus_excluded", b, e),
                                 ("target_selection_shift", c, b), ("total_four_target_shift", c, a)):
            row[key] = left - right if left is not None and right is not None else None
        for key, value in row.items():
            if value is not None:
                distributions[key].append(value)
    return distributions


def main():
    checks, errors = [], []

    def check(name, action):
        try:
            action()
            checks.append(name)
        except Exception as exc:
            errors.append({"check": name, "error": f"{type(exc).__name__}: {exc}"})

    eligibility = [True] * 19 + [False] * 26
    draws = np.random.default_rng(90210).integers(0, 45, size=(257, 45))

    def composition_reversal():
        values = [-.03] * 19 + [.05] * 26
        four = [-.02] * 19 + [None] * 26
        result = summarise(values, eligibility, draws, four)
        est = result["estimates"]
        assert abs(est["all"]["mean_difference"] - 0.01622222222222222) < 1e-12
        assert abs(est["eligible"]["mean_difference"] + .03) < 1e-12
        assert abs(est["excluded"]["mean_difference"] - .05) < 1e-12
        assert abs(est["target_selection_shift"]["mean_difference"] - .01) < 1e-12
        assert result["point_estimate_sign_changes"]["eligible_vs_all"]
        assert result["point_estimate_sign_changes"]["four_targets_vs_all"]
        assert abs(result["composition_identity"]["residual"]) < 1e-12
        assert abs(result["shift_identity_residual"]) < 1e-12

    check("Synthetic 19/26 patient composition can change comparison sign; two shifts conserve the difference", composition_reversal)

    def uniform_effect():
        result = summarise([.01] * 45, eligibility, draws, [.01] * 19 + [None] * 26)
        assert not any(result["point_estimate_sign_changes"].values())
        for key in ("patient_selection_shift", "eligible_minus_excluded", "target_selection_shift", "total_four_target_shift"):
            assert abs(result["estimates"][key]["mean_difference"]) < 1e-12

    check("Uniform patient effects do not produce a selection sign change", uniform_effect)

    def null_and_scalar_bootstrap():
        values = [None] + [-.03 + i / 1000 for i in range(1, 19)] + [.05 - i / 1000 for i in range(26)]
        four = [None] + [-.01 + i / 1500 for i in range(1, 19)] + [None] * 26
        result = summarise(values, eligibility, draws, four)
        assert result["group_counts"]["all"]["finite_patients"] == 44
        assert result["group_counts"]["eligible"]["finite_patients"] == 18
        assert abs(result["composition_identity"]["eligible_fraction_of_finite_all"] - 18 / 44) < 1e-12
        reference = scalar_bootstrap(values, eligibility, four, draws)
        for key, distribution in reference.items():
            estimate = result["estimates"][key]
            assert estimate["valid_bootstrap_draws"] == len(distribution)
            expected = [percentile_scalar(distribution, q) for q in (2.5, 97.5)]
            assert all(abs(a - b) < 1e-12 for a, b in zip(expected, estimate["ci95_percentile"]))

    check("Empty lesion stays undefined; shared resampling matches independent scalar loop and percentile", null_and_scalar_bootstrap)

    def absent_group():
        tiny_draws = np.array([[0, 0], [1, 1], [0, 1]])
        result = summarise([1., 3.], [True, False], tiny_draws, [2., None])
        assert result["estimates"]["eligible"]["undefined_bootstrap_draws"] == 1
        assert result["estimates"]["excluded"]["undefined_bootstrap_draws"] == 1
        assert result["estimates"]["eligible_minus_excluded"]["valid_bootstrap_draws"] == 1
        assert result["estimates"]["eligible_minus_excluded"]["ci95_percentile"] == [-2., -2.]

    check("Absent bootstrap groups retain undefined repeats rather than zero", absent_group)

    def target_aggregation():
        record = {"per_plane_image_errors": [
            {"z": z, "support": {"pixels": n, "sse": sse, "nmse": sse / n}}
            for z, n, sse in ((1, 1, 2), (3, 3, 3), (5, 2, 6), (7, 4, 20), (9, 2, 100))]}
        assert selected_image(record, "support", "target_equal_nmse", [1, 3, 5, 7]) == 2.75
        assert selected_image(record, "support", "pixel_weighted_nmse", [1, 3, 5, 7]) == 3.1
        for indices in ([1, 3, 5, 5], [1, 3, 5, 11]):
            try:
                selected_image(record, "support", "target_equal_nmse", indices)
            except ValueError:
                continue
            raise AssertionError("Invalid or repeated target was accepted")

    check("Four-target SSE/pixel aggregation excludes other targets and rejects duplicates or missing targets", target_aggregation)

    def reject_partial_cohort():
        for roster in ([str(i) for i in range(44)], [str(i) for i in range(45)]):
            try:
                analyse({}, {}, roster)
            except ValueError:
                continue
            raise AssertionError("Incomplete fixed cohort was accepted")

    check("44/45 patients or missing endpoint records cannot enter analysis", reject_partial_cohort)
    def synthetic_full_schema():
        roster = [f"synthetic-{i:02d}" for i in range(45)]
        records, coverage = {}, {}
        names = ("native", "raw_linear", "raw_pchip", "pipeline_linear", "pipeline_pchip", "hat", "swinir")
        for i, patient in enumerate(roster):
            coverage[patient] = {"labels": {kind: {"old_target_rule_eligible": i < count,
                "selected_four_indices": [1, 3, 5, 7] if i < count else []}
                for kind, count in (("original_json", 19), ("rtstruct", 18))}}
            records[patient] = {}
            for name in names:
                value = .002 if name == "hat" else .004
                dice = .8 if name == "hat" else .75
                regions = ("support", "original_json_lesion", "rtstruct_lesion")
                image = {r: {"target_equal_nmse": value, "pixel_weighted_nmse": value} for r in regions}
                planes = [{"z": z, **{r: {"pixels": 10, "sse": 10 * value, "nmse": value} for r in regions}}
                          for z in (1, 3, 5, 7, 9)]
                task = {kind: {domain: {"dice": dice, "absolute_relative_volume_error": .1}
                    for domain in ("full", "observed_anchor_slab")} for kind in ("original_json", "rtstruct")}
                records[patient][name] = {"image_metrics": image, "per_plane_image_errors": planes, "task_metrics": task}
        result = analyse(records, coverage, roster)
        assert len(result["endpoints"]) == 112
        for row in result["endpoints"]:
            point = row["estimates"]["all"]["mean_difference"]
            expected = -.002 if row["kind"] == "image" else .05 if row["endpoint"].endswith("/dice") else 0.
            expected = expected if row["model"] == "hat" else 0.
            assert abs(point - expected) < 1e-12
            assert row["estimates"]["all"]["valid_bootstrap_draws"] == 5000
            expected_n = 19 if row["label_and_qualification"] == "original_json" else 18
            assert row["group_counts"]["eligible"]["finite_patients"] == expected_n
            assert not any(row["point_estimate_sign_changes"].values())
        assert not result["primary_claim_changed"] and not result["publication_claim_confirmed"]

    check("Synthetic complete seven-condition schema yields all 112 fixed secondary endpoints without effect selection", synthetic_full_schema)
    report = {"complete": not errors, "checks": checks, "errors": errors, "script_sha256": sha(Path(__file__)),
              "analysis_script_sha256": sha(Path(__file__).with_name("vs_seg_selection_sensitivity.py")),
              "patient_effect_records_read": False, "simulated_outcomes_are_scientific_evidence": False, "gpu_used": False}
    write(OUT / "development_checks.json", report)
    print(__import__("json").dumps(report, ensure_ascii=False))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
