"""Independent, read-only audit of the strongest existing RASINet evidence.

This script reads immutable artifacts under design/rasinet and writes only to
design/paper.  It intentionally does not recompute model predictions.
"""

from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "rasinet" / "outputs" / "nested_optimization"
OUT = HERE / "audit_outputs"


def rows(name: str):
    with (SOURCE / name).open("r", encoding="utf-8-sig", newline="") as f:
        yield from csv.DictReader(f)


def f(value: str) -> float:
    return float(value)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    finalist = list(rows("nested_finalist_results.csv"))
    by_method = Counter(r["method"] for r in finalist)
    check("nine fixed profiles per finalist", all(v == 9 for v in by_method.values()), dict(by_method))
    check("all finalist profiles contain 22 outer cases", all(int(r["n"]) == 22 for r in finalist), len(finalist))

    aggregate = list(rows("nested_aggregate_results.csv"))
    overall = {r["method"]: r for r in aggregate if r["level"] == "overall" and r["key"] == "all"}
    expected = {
        "frozen_baseline": 0.07720943634539858,
        "physical_consistency": 0.051570748071521455,
        "frozen_plus_physical": 0.05042679397106439,
        "nested_triage": 0.2703588627331229,
        "robust_nested_triage": 0.29856177609605467,
    }
    for method, value in expected.items():
        observed = f(overall[method]["normalized_aurc"])
        check(f"aggregate nAURC: {method}", math.isclose(observed, value, rel_tol=0, abs_tol=1e-12), observed)

    paired = list(rows("profile_aligned_paired_summary.csv"))
    physical_delta = next(
        r for r in paired
        if r["level"] == "overall" and r["key"] == "all"
        and r["method"] == "physical_consistency" and r["comparator"] == "frozen_baseline"
    )
    delta = f(physical_delta["delta_normalized_aurc"])
    lo = f(physical_delta["delta_normalized_aurc_lo"])
    hi = f(physical_delta["delta_normalized_aurc_hi"])
    check("physical consistency paired nAURC CI excludes zero", delta < 0 and hi < 0, {"delta": delta, "lo": lo, "hi": hi})

    hybrid_delta = next(
        r for r in paired
        if r["level"] == "overall" and r["key"] == "all"
        and r["method"] == "frozen_plus_physical" and r["comparator"] == "physical_consistency"
    )
    hlo = f(hybrid_delta["delta_normalized_aurc_lo"])
    hhi = f(hybrid_delta["delta_normalized_aurc_hi"])
    check("hybrid is not distinguishable from physical consistency", hlo <= 0 <= hhi, {"lo": hlo, "hi": hhi})

    physical = list(rows("cross_scale_physical_pair_scores.csv"))
    matched = [r for r in physical if r["status"] == "matched_physical_planes"]
    check("all physical records matched", len(physical) == 1518 and len(matched) == len(physical), len(matched))
    check("physical plane tolerance respected", max(f(r["max_plane_distance_mm"]) for r in physical) <= 0.001, max(f(r["max_plane_distance_mm"]) for r in physical))
    check("matched support nonempty", min(int(r["matched_generated_planes"]) for r in physical) > 0, min(int(r["matched_generated_planes"]) for r in physical))

    predictions = list(rows("all_finalist_outer_predictions.csv"))
    prediction_counts = Counter(r["method"] for r in predictions)
    check("complete 9x22 outer predictions per finalist", all(v == 198 for v in prediction_counts.values()), dict(prediction_counts))

    candidate_count = sum(1 for _ in rows("candidate_registry.csv"))
    check("full candidate registry retained", candidate_count == 561_492, candidate_count)

    manifests = {
        "unconstrained": list(rows("ningxia_nested_selection_manifest.csv")),
        "amended": list(rows("ningxia_robust_selection_manifest.csv")),
        "attribution": list(rows("target_attribution_selection_manifest.csv")),
    }
    for label, manifest in manifests.items():
        check(f"{label} selection never uses outer labels", all(r["selection_used_outer_labels"].lower() == "false" for r in manifest), len(manifest))
        if "target_model" in manifest[0]:
            excluded = all(r["target_model"] not in set(r["members"].split(";")) for r in manifest)
            check(f"{label} selection excludes target identity", excluded, len(manifest))
    unconstrained_analytic = sum(
        set(r["members"].split(";")) <= {"linear", "cubic"}
        for r in manifests["unconstrained"]
    )
    check("unconstrained selector exposes analytical-only collapse", unconstrained_analytic > 0, unconstrained_analytic)

    attribution = [r for r in rows("target_attribution_nested_results.csv") if r["role"] == "nested_attribution"]
    mean_adv = sum(f(r["matched_advantage"]) for r in attribution) / len(attribution)
    mean_within = sum(f(r["within_case_spearman"]) for r in attribution) / len(attribution)
    mean_top1 = sum(f(r["top1_accuracy"]) for r in attribution) / len(attribution)
    check("target attribution remains weak", mean_within < 0.2 and mean_top1 < 1 / 3, {"matched_advantage": mean_adv, "within_case_spearman": mean_within, "top1_accuracy": mean_top1})

    with (OUT / "evidence_audit.json").open("w", encoding="utf-8") as fobj:
        json.dump({"source": str(SOURCE), "checks": checks}, fobj, indent=2, ensure_ascii=False)
    with (OUT / "evidence_audit.csv").open("w", encoding="utf-8", newline="") as fobj:
        writer = csv.DictWriter(fobj, fieldnames=["check", "passed", "detail"])
        writer.writeheader()
        writer.writerows(checks)

    failed = [c for c in checks if not c["passed"]]
    print(json.dumps({"checks": len(checks), "failed": failed}, indent=2, ensure_ascii=False))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
