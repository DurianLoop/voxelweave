from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .icassp_statistics import ranking_metrics
from .nested_selection import candidate_scores, empirical_cdf
from .optimization_protocol import ANALYTICAL, UNIVERSAL_NEURAL


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs" / "nested_optimization"


def jackknife_se(errors: np.ndarray, scores: np.ndarray) -> float:
    values = []
    for index in range(len(errors)):
        keep = np.arange(len(errors)) != index
        values.append(ranking_metrics(errors[keep], scores[keep])["normalized_aurc"])
    values = np.asarray(values, dtype=float)
    return float(np.sqrt((len(values) - 1) / len(values) * np.sum((values - values.mean()) ** 2)))


def neural_count(members: str) -> int:
    return sum(member not in ANALYTICAL for member in members.split(";"))


def main() -> None:
    pairs = pd.read_csv(OUT / "pair_features_per_case_ningxia.csv")
    errors = pd.read_csv(OUT / "common_errors_per_case_ningxia.csv")
    registry = pd.read_csv(OUT / "candidate_registry.csv")
    retained = registry[registry.selected_for_nested.astype(str).str.lower().eq("true")].copy()
    retained["neural_member_count"] = retained.members.map(neural_count)
    folds = sorted(pairs.fold.unique())
    manifests, inner_rows, predictions = [], [], []

    for scale in (2, 4, 6):
        for target in UNIVERSAL_NEURAL:
            group = pairs[pairs.scale.eq(scale) & pairs.target_model.eq(target)]
            candidates = retained[retained.scale.eq(scale) & retained.target_model.eq(target)]
            score_lookup = candidate_scores(group, candidates)
            error = errors[errors.scale.eq(scale) & errors.target_model.eq(target)].set_index("case")
            fold_by_case = group.drop_duplicates("case").set_index("case").fold
            for outer in folds:
                inner_cases = sorted(fold_by_case[fold_by_case.ne(outer)].index)
                outer_cases = sorted(fold_by_case[fold_by_case.eq(outer)].index)
                rows = []
                for candidate in candidates.itertuples(index=False):
                    scores = score_lookup[candidate.candidate_id]
                    pooled = ranking_metrics(error.loc[inner_cases].common_error.to_numpy(), scores.loc[inner_cases].to_numpy())
                    fold_values = []
                    for inner_fold in folds:
                        if inner_fold == outer:
                            continue
                        cases = [case for case in inner_cases if fold_by_case.loc[case] == inner_fold]
                        if len(cases) >= 2:
                            fold_values.append(ranking_metrics(error.loc[cases].common_error.to_numpy(), scores.loc[cases].to_numpy())["normalized_aurc"])
                    fold_values = np.asarray(fold_values, dtype=float)
                    rows.append({
                        "outer_fold": outer, "scale": scale, "target_model": target,
                        "candidate_id": candidate.candidate_id,
                        "pooled_inner_nAURC": pooled["normalized_aurc"],
                        "public_development_nAURC": candidate.normalized_aurc,
                        "worst_inner_nAURC": float(np.max(fold_values)),
                        "std_inner_nAURC": float(np.std(fold_values)),
                        "neural_member_count": candidate.neural_member_count,
                        "committee_size": candidate.committee_size,
                        "cost_proxy": candidate.cost_proxy,
                        "formula_complexity": candidate.formula_complexity,
                    })
                summary = pd.DataFrame(rows)
                summary["selection_J"] = 0.0
                for metric, weight in (("pooled_inner_nAURC", 1.0), ("public_development_nAURC", 0.5),
                                       ("worst_inner_nAURC", 0.5), ("std_inner_nAURC", 0.25),
                                       ("cost_proxy", 0.1)):
                    summary[f"rank_{metric}"] = summary[metric].rank(method="min")
                    summary["selection_J"] += weight * summary[f"rank_{metric}"]

                pools = {
                    "robust_nested_triage": summary[summary.neural_member_count.ge(2)],
                    "robust_nested_low_cost": summary[
                        summary.neural_member_count.between(1, 2) & summary.committee_size.le(3)
                    ],
                }
                summary["selected_robust_main"] = False
                summary["selected_robust_low_cost"] = False
                for role, pool in pools.items():
                    objective_best = pool.sort_values("selection_J").iloc[0]
                    best_scores = score_lookup[objective_best.candidate_id].loc[inner_cases].to_numpy()
                    se = jackknife_se(error.loc[inner_cases].common_error.to_numpy(), best_scores)
                    threshold = objective_best.pooled_inner_nAURC + se
                    eligible = pool[pool.pooled_inner_nAURC.le(threshold + 1e-12)]
                    chosen = eligible.sort_values([
                        "neural_member_count", "cost_proxy", "committee_size",
                        "formula_complexity", "selection_J"
                    ]).iloc[0]
                    selected_column = "selected_robust_main" if role == "robust_nested_triage" else "selected_robust_low_cost"
                    summary.loc[summary.candidate_id.eq(chosen.candidate_id), selected_column] = True
                    candidate = candidates[candidates.candidate_id.eq(chosen.candidate_id)].iloc[0]
                    manifests.append({
                        "role": role, "outer_fold": outer, "scale": scale, "target_model": target,
                        "candidate_id": chosen.candidate_id, "feature": candidate.feature,
                        "members": candidate.members, "weight_mode": candidate.weight_mode,
                        "weights": candidate.weights, "inner_case_count": len(inner_cases),
                        "outer_case_count": len(outer_cases), "one_se_threshold": threshold,
                        "selected_pooled_inner_nAURC": chosen.pooled_inner_nAURC,
                        "selected_public_development_nAURC": chosen.public_development_nAURC,
                        "selection_used_outer_labels": False, "protocol_status": "post-audit_amendment",
                    })
                    raw = score_lookup[chosen.candidate_id]
                    calibrated = empirical_cdf(raw.loc[inner_cases].to_numpy(), raw.loc[outer_cases].to_numpy())
                    for case, value in zip(outer_cases, calibrated):
                        predictions.append({
                            "method": role, "outer_fold": outer, "scale": scale, "case": case,
                            "target_model": target, "candidate_id": chosen.candidate_id,
                            "raw_score": raw.loc[case], "triage_score": value,
                            "common_error": error.loc[case, "common_error"],
                            "protocol_status": "post-audit_amendment",
                        })
                inner_rows.extend(summary.to_dict("records"))

    manifest = pd.DataFrame(manifests)
    inner = pd.DataFrame(inner_rows)
    pred = pd.DataFrame(predictions)
    manifest.to_csv(OUT / "ningxia_robust_selection_manifest.csv", index=False)
    inner.to_csv(OUT / "ningxia_robust_inner_selection_results.csv", index=False)
    pred.to_csv(OUT / "ningxia_robust_predictions.csv", index=False)
    result = []
    for (method, scale, target), group in pred.groupby(["method", "scale", "target_model"]):
        result.append({"method": method, "scale": scale, "target_model": target, "n": len(group),
                       **ranking_metrics(group.common_error.to_numpy(), group.triage_score.to_numpy())})
    pd.DataFrame(result).to_csv(OUT / "ningxia_robust_outer_fold_results.csv", index=False)
    print(f"robust manifests={len(manifest)} outer predictions={len(pred)}")


if __name__ == "__main__":
    main()
