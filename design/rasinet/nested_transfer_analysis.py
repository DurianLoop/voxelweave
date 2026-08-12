from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .icassp_statistics import ranking_metrics
from .nested_selection import candidate_scores, score_from_matrix
from .optimization_protocol import UNIVERSAL_NEURAL


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs" / "nested_optimization"


def evaluate_spec(group: pd.DataFrame, spec: pd.Series) -> pd.Series:
    members = spec.members.split(";")
    matrix = group.pivot(index="case", columns="member", values=spec.feature)[members]
    weights = np.asarray([float(value) for value in spec.weights.split(";")])
    values = score_from_matrix(matrix.to_numpy(), list(range(len(members))), weights, spec.weight_mode)
    return pd.Series(values, index=matrix.index)


def metric_for(group: pd.DataFrame, errors: pd.DataFrame, spec: pd.Series) -> dict[str, float]:
    scores = evaluate_spec(group, spec)
    truth = errors.set_index("case").loc[scores.index, "common_error"]
    return ranking_metrics(truth.to_numpy(), scores.to_numpy())


def metrics_for_pool(group: pd.DataFrame, errors: pd.DataFrame, pool: pd.DataFrame) -> dict[str, dict[str, float]]:
    lookup = candidate_scores(group, pool)
    truth = errors.set_index("case").common_error
    return {
        candidate_id: ranking_metrics(truth.loc[scores.index].to_numpy(), scores.to_numpy())
        for candidate_id, scores in lookup.items()
    }


def main() -> None:
    registry = pd.read_csv(OUT / "candidate_registry.csv")
    interactions = pd.read_csv(OUT / "score_committee_interaction_results.csv")
    candidates = registry[registry.weight_mode.isin(["uniform", "trim_max"])].copy()
    max_size = candidates.groupby(["scale", "target_model"]).committee_size.transform("max")
    # Data-independent representative transfer pool: all two-member and full
    # committees for every score family, under uniform or trimmed aggregation.
    candidates = candidates[candidates.committee_size.eq(2) | candidates.committee_size.eq(max_size)].copy()
    candidates["structure"] = (
        candidates.feature + "|" + candidates.members + "|" + candidates.weight_mode
    )
    pairs = {
        "fastmri": pd.read_csv(OUT / "pair_features_per_case_development.csv").query("dataset == 'fastmri'"),
        "ningxia": pd.read_csv(OUT / "pair_features_per_case_ningxia.csv"),
    }
    errors = {
        "fastmri": pd.read_csv(OUT / "common_errors_per_case_development.csv").query("dataset == 'fastmri'"),
        "ningxia": pd.read_csv(OUT / "common_errors_per_case_ningxia.csv"),
    }
    records = []

    # fastMRI -> NingXia uses the frozen public metric and never consults the
    # NingXia endpoint when selecting the candidate.
    for scale in (2, 4, 6):
        for target in UNIVERSAL_NEURAL:
            pool = interactions[
                interactions.scale.eq(scale)
                & interactions.target_model.eq(target)
                & interactions.weight_mode.isin(["uniform", "trim_max"])
            ]
            selected = pool.sort_values(["normalized_aurc", "neural_member_count", "formula_complexity"]).iloc[0]
            test_group = pairs["ningxia"].query("scale == @scale and target_model == @target")
            test_error = errors["ningxia"].query("scale == @scale and target_model == @target")
            metrics = metric_for(test_group, test_error, selected)
            records.append({"analysis":"fastmri_to_ningxia", "selection_scales":str(scale),
                            "test_dataset":"ningxia", "test_scale":scale, "target_model":target,
                            "candidate_id":selected.candidate_id, **metrics})

    # NingXia -> fastMRI is explicitly retrospective. Candidate definitions
    # are data-independent uniform/trimmed structures; no fastMRI endpoint is
    # used to choose among them in this direction.
    for scale in (2, 4, 6):
        for target in UNIVERSAL_NEURAL:
            pool = candidates[candidates.scale.eq(scale) & candidates.target_model.eq(target)]
            train_group = pairs["ningxia"].query("scale == @scale and target_model == @target")
            train_error = errors["ningxia"].query("scale == @scale and target_model == @target")
            train_metrics = metrics_for_pool(train_group, train_error, pool)
            selected_id = min(train_metrics, key=lambda candidate_id: train_metrics[candidate_id]["normalized_aurc"])
            selected = pool[pool.candidate_id.eq(selected_id)].iloc[0]
            test_group = pairs["fastmri"].query("scale == @scale and target_model == @target")
            test_error = errors["fastmri"].query("scale == @scale and target_model == @target")
            metrics = metric_for(test_group, test_error, selected)
            records.append({"analysis":"ningxia_to_fastmri_retrospective", "selection_scales":str(scale),
                            "test_dataset":"fastmri", "test_scale":scale, "target_model":target,
                            "candidate_id":selected.candidate_id, **metrics})

    # Leave-one-scale-out transfer selects one common structure using two
    # source scales, then instantiates that structure at the held scale.
    for dataset in ("fastmri", "ningxia"):
        for held in (2, 4, 6):
            source_scales = sorted({2, 4, 6} - {held})
            for target in UNIVERSAL_NEURAL:
                available = candidates[candidates.target_model.eq(target)]
                common_structures = set.intersection(*[
                    set(available[available.scale.eq(scale)].structure) for scale in (2, 4, 6)
                ])
                metric_cache = {}
                for scale in source_scales:
                    scale_pool = available[available.scale.eq(scale) & available.structure.isin(common_structures)]
                    group = pairs[dataset].query("scale == @scale and target_model == @target")
                    error = errors[dataset].query("scale == @scale and target_model == @target")
                    by_id = metrics_for_pool(group, error, scale_pool)
                    metric_cache[scale] = {
                        row.structure: by_id[row.candidate_id]["normalized_aurc"]
                        for row in scale_pool.itertuples(index=False)
                    }
                ranked = [(float(np.mean([metric_cache[scale][structure] for scale in source_scales])), structure)
                          for structure in common_structures]
                selected_structure = min(ranked)[1]
                selected = available[available.scale.eq(held) & available.structure.eq(selected_structure)].iloc[0]
                test_group = pairs[dataset].query("scale == @held and target_model == @target")
                test_error = errors[dataset].query("scale == @held and target_model == @target")
                metrics = metric_for(test_group, test_error, selected)
                records.append({"analysis":"leave_one_scale_out_retrospective", "selection_scales":"+".join(map(str,source_scales)),
                                "test_dataset":dataset, "test_scale":held, "target_model":target,
                                "candidate_id":selected.candidate_id, **metrics})

    pd.DataFrame(records).to_csv(OUT / "frozen_transfer_results.csv", index=False)
    print(f"transfer records={len(records)}")


if __name__ == "__main__":
    main()
