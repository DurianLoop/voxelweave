"""Endpoint sensitivity, consistent-but-wrong cases, and TTA paired checks."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "plan2_outputs"
sys.path.insert(0, str(ROOT / "design"))
from rasinet.icassp_statistics import ranking_metrics  # noqa: E402

TARGETS = ("i3net", "hat", "swinir")


def endpoint_sensitivity() -> tuple[pd.DataFrame, pd.DataFrame]:
    context = pd.read_csv(OUT / "context_controls" / "per_case.csv")
    context = context[context.variant.isin(["raw", "pooled_dynamic_range"]) & ~context.scale.astype(str).str.startswith("pair_")].copy()
    context.scale = context.scale.astype(int)
    base = pd.read_csv(ROOT / "design" / "rasinet" / "outputs" / "multiscale" / "per_case_scores.csv")
    base = base[base.dataset.eq("fastmri") & base.target.isin(TARGETS) & base.method.eq("target_median")]
    base = base[["scale", "case_id", "target", "case_score"]]
    base.columns = ["scale", "case", "target_model", "score"]
    labels = context[context.variant.eq("raw")][["scale", "case", "target_model", "common_error", "range_normalized_error"]]
    base = base.merge(labels, on=["scale", "case", "target_model"])
    base["variant"] = "frozen_baseline"
    pc = context.rename(columns={"variant": "variant"})[["scale", "case", "target_model", "score", "common_error", "range_normalized_error", "variant"]]
    frame = pd.concat([base, pc], ignore_index=True)
    rows = []
    for (variant, scale, target), group in frame.groupby(["variant", "scale", "target_model"]):
        for endpoint in ("common_error", "range_normalized_error"):
            values = ranking_metrics(group[endpoint], group.score)
            rows.append({"variant": variant, "endpoint": endpoint, "scale": scale, "target_model": target, **values})
    result = pd.DataFrame(rows)
    result.to_csv(OUT / "endpoint_sensitivity_profiles.csv", index=False)
    aggregate = result.groupby(["variant", "endpoint"], as_index=False)[["normalized_aurc", "case_spearman", "case_kendall", "rrr_50"]].mean()
    aggregate.to_csv(OUT / "endpoint_sensitivity_aggregate.csv", index=False)
    return aggregate, frame


def clustered_endpoint_comparison(frame: pd.DataFrame, samples: int = 2000) -> dict[str, object]:
    selected = frame[frame.variant.isin(["frozen_baseline", "pooled_dynamic_range"])].copy()
    cases = np.asarray(sorted(selected.case.unique()))
    by_case = {case: selected[selected.case.eq(case)] for case in cases}

    def delta(data: pd.DataFrame) -> float:
        rows = []
        for (variant, scale, target), group in data.groupby(["variant", "scale", "target_model"]):
            rows.append({"variant": variant, "value": ranking_metrics(group.range_normalized_error, group.score)["normalized_aurc"]})
        means = pd.DataFrame(rows).groupby("variant").value.mean()
        return float(means["pooled_dynamic_range"] - means["frozen_baseline"])

    observed = delta(selected)
    rng = np.random.default_rng(20260815)
    values = []
    for _ in range(samples):
        parts = []
        for draw, case in enumerate(rng.choice(cases, len(cases), replace=True)):
            part = by_case[case].copy(); part["case"] = f"draw_{draw}"; parts.append(part)
        values.append(delta(pd.concat(parts, ignore_index=True)))
    return {"delta_normalized_aurc": observed, "cluster_bootstrap_95ci": [float(np.quantile(values, .025)), float(np.quantile(values, .975))], "samples": samples}


def consistent_wrong(dataset: str) -> pd.DataFrame:
    if dataset == "fastmri":
        pc = pd.read_csv(ROOT / "design" / "rasinet" / "outputs" / "nested_optimization" / "cross_scale_consistency_per_case.csv")
        pc = pc[pc.dataset.eq("fastmri") & pc.target_model.isin(TARGETS)]
        frame = pc[["case", "scale", "target_model", "common_error", "consistency"]].rename(columns={"consistency": "pc_score"})
    else:
        allpred = pd.read_csv(ROOT / "design" / "rasinet" / "outputs" / "nested_optimization" / "all_finalist_outer_predictions.csv")
        frame = allpred[allpred.method.eq("physical_consistency")][["case", "scale", "target_model", "common_error", "triage_score"]].rename(columns={"triage_score": "pc_score"})
    frame["error_pct"] = frame.groupby(["scale", "target_model"]).common_error.rank(pct=True)
    frame["pc_pct"] = frame.groupby(["scale", "target_model"]).pc_score.rank(pct=True)
    failures = frame[(frame.error_pct >= 0.75) & (frame.pc_pct <= 0.25)].copy()
    failures["dataset"] = dataset
    failures.to_csv(OUT / f"{dataset}_consistent_but_wrong.csv", index=False)
    return failures


def tta_permutation(samples: int = 10000) -> dict[str, object]:
    frame = pd.read_csv(OUT / "fastmri_x4_swinir_comparator_per_case.csv")
    methods = ("tta", "physical_consistency")
    for method in methods:
        frame[method] = frame[method].rank(method="average")
    observed = {m: ranking_metrics(frame.common_error, frame[m]) for m in methods}
    obs_delta = observed["physical_consistency"]["normalized_aurc"] - observed["tta"]["normalized_aurc"]
    rng = np.random.default_rng(20260814)
    null = []
    for _ in range(samples):
        mask = rng.random(len(frame)) < 0.5
        a, b = frame.tta.to_numpy().copy(), frame.physical_consistency.to_numpy().copy()
        a[mask], b[mask] = b[mask], a[mask]
        null.append(ranking_metrics(frame.common_error, b)["normalized_aurc"] - ranking_metrics(frame.common_error, a)["normalized_aurc"])
    p = float((1 + np.sum(np.abs(null) >= abs(obs_delta))) / (samples + 1))
    return {"delta_pc_minus_tta_nAURC": obs_delta, "two_sided_p": p, "samples": samples}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    aggregate, endpoint_frame = endpoint_sensitivity()
    failures = {dataset: consistent_wrong(dataset) for dataset in ("ningxia", "fastmri")}
    payload = {
        "endpoint_sensitivity": aggregate.to_dict("records"),
        "normalized_endpoint_cluster_comparison": clustered_endpoint_comparison(endpoint_frame),
        "consistent_but_wrong_counts": {k: len(v) for k, v in failures.items()},
        "tta_permutation": tta_permutation(),
    }
    (OUT / "boundary_summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
