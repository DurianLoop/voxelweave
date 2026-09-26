"""P11-E03: reflection-matched physical-anchor identity-swap analysis."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve()
P11 = HERE.parents[1]
OUT = P11 / "outputs"
SEED = 20260827


def paired_plane_effects(planes: pd.DataFrame) -> pd.DataFrame:
    keys = ["dataset", "case", "patient_cluster", "model", "family", "target_z", "target_residue"]
    value_columns = [
        "observable_error_fraction",
        "shared_error_fraction",
        "error_cosine",
        "prediction_disagreement_mae",
        "paired_error_mae",
    ]
    wide = planes.pivot(index=keys, columns="condition", values=value_columns)
    wide.columns = [f"{metric}_{condition}" for metric, condition in wide.columns]
    wide = wide.reset_index()
    wide["identity_minus_shared_observable"] = wide.observable_error_fraction_disjoint - wide.observable_error_fraction_shared
    wide["identity_minus_shared_fraction"] = wide.shared_error_fraction_disjoint - wide.shared_error_fraction_shared
    wide["identity_minus_shared_error_cosine"] = wide.error_cosine_disjoint - wide.error_cosine_shared
    wide["identity_minus_shared_disagreement"] = wide.prediction_disagreement_mae_disjoint - wide.prediction_disagreement_mae_shared
    wide["geometry_equivalence"] = "nearest-anchor distances {1,3}, left-right reflected"
    wide["same_target"] = True
    wide["same_model"] = True
    wide["same_anchor_count"] = True
    wide["same_stride"] = True
    wide["physical_anchor_identity"] = "disjoint"
    return wide


def balanced_case_effects(effects: pd.DataFrame) -> pd.DataFrame:
    by_residue = (
        effects.groupby(["dataset", "case", "patient_cluster", "model", "family", "target_residue"], as_index=False)
        .agg(
            observable_gain=("identity_minus_shared_observable", "median"),
            shared_fraction_change=("identity_minus_shared_fraction", "median"),
            error_cosine_change=("identity_minus_shared_error_cosine", "median"),
            disagreement_change=("identity_minus_shared_disagreement", "median"),
            targets=("target_z", "nunique"),
        )
    )
    metrics = ["observable_gain", "shared_fraction_change", "error_cosine_change", "disagreement_change"]
    records = []
    for keys, g in by_residue.groupby(["dataset", "case", "patient_cluster", "model", "family"]):
        residues = set(g.target_residue.astype(int))
        if residues != {1, 3}:
            continue
        row = dict(zip(["dataset", "case", "patient_cluster", "model", "family"], keys))
        for metric in metrics:
            values = g.set_index("target_residue")[metric]
            row[f"{metric}_residue1"] = float(values.loc[1])
            row[f"{metric}_residue3"] = float(values.loc[3])
            row[f"{metric}_balanced"] = float(0.5 * (values.loc[1] + values.loc[3]))
            row[f"{metric}_mirror_difference"] = float(values.loc[1] - values.loc[3])
        row["targets_residue1"] = int(g.set_index("target_residue").loc[1, "targets"])
        row["targets_residue3"] = int(g.set_index("target_residue").loc[3, "targets"])
        records.append(row)
    return pd.DataFrame(records)


def bootstrap_models(case_df: pd.DataFrame, models: list[str], samples: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for model in models:
        g = case_df[case_df.model.eq(model)].reset_index(drop=True)
        if g.empty:
            continue
        values = g.observable_gain_balanced.to_numpy(float)
        mirror = g.observable_gain_mirror_difference.to_numpy(float)
        gain_reps, mirror_reps = [], []
        for _ in range(samples):
            idx = rng.integers(0, len(g), len(g))
            gain_reps.append(float(np.median(values[idx])))
            mirror_reps.append(float(np.median(mirror[idx])))
        rows.append(
            {
                "model": model,
                "family": g.family.iloc[0],
                "cases_with_both_mirror_classes": len(g),
                "median_balanced_observable_gain": float(np.median(values)),
                "gain_ci_low": float(np.percentile(gain_reps, 2.5)),
                "gain_ci_high": float(np.percentile(gain_reps, 97.5)),
                "fraction_cases_positive": float(np.mean(values > 0)),
                "median_residue1_minus_residue3": float(np.median(mirror)),
                "mirror_difference_ci_low": float(np.percentile(mirror_reps, 2.5)),
                "mirror_difference_ci_high": float(np.percentile(mirror_reps, 97.5)),
                "orientation_warning": bool((np.percentile(mirror_reps, 2.5) > 0) or (np.percentile(mirror_reps, 97.5) < 0)),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-suffix", default="")
    parser.add_argument("--output-suffix", default="")
    parser.add_argument("--models", nargs="+", default=None)
    parser.add_argument("--bootstrap", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()

    input_suffix = f"_{args.input_suffix}" if args.input_suffix else ""
    output_suffix = f"_{args.output_suffix}" if args.output_suffix else input_suffix
    source = OUT / f"p11_ixi_clean_per_plane{input_suffix}.csv"
    if not source.exists():
        raise FileNotFoundError(f"Run P11-E02 first: {source}")
    planes = pd.read_csv(source)
    models = args.models or sorted(planes.model.unique())
    planes = planes[planes.model.isin(models)].copy()
    required_conditions = set(planes.condition.unique())
    if required_conditions != {"shared", "disjoint"}:
        raise RuntimeError(f"Expected shared/disjoint rows, found {required_conditions}")
    if not planes.nearest_distance_multiset.astype(str).eq("1;3").all():
        raise RuntimeError("Geometry gate failed: not every row has nearest-distance multiset {1,3}")

    effects = paired_plane_effects(planes)
    case_df = balanced_case_effects(effects)
    summaries = bootstrap_models(case_df, models, args.bootstrap, args.seed)
    effects.to_csv(OUT / f"p11_identity_swap_per_plane{output_suffix}.csv", index=False)
    case_df.to_csv(OUT / f"p11_identity_swap_balanced_per_case{output_suffix}.csv", index=False)
    summaries.to_csv(OUT / f"p11_identity_swap_model_summary{output_suffix}.csv", index=False)
    payload = {
        "experiment": "P11-E03 reflection-matched geometry identity swap",
        "status": "PILOT" if "smoke" in output_suffix.lower() else "FROZEN ANALYSIS",
        "source": source.name,
        "models": models,
        "bootstrap": args.bootstrap,
        "seed": args.seed,
        "geometry_gate": {
            "same_target": True,
            "same_model": True,
            "same_anchor_count": True,
            "same_stride": True,
            "nearest_distance_multiset": [1, 3],
            "signed_geometry": "left-right reflected, not identical",
            "physical_anchor_identity": "disjoint",
        },
        "all_model_gain_intervals_positive": bool(len(summaries) == len(models) and (summaries.gain_ci_low > 0).all()),
        "models_with_orientation_warning": summaries.loc[summaries.orientation_warning, "model"].tolist(),
        "eligible_balanced_cases": int(len(case_df)),
    }
    (OUT / f"p11_identity_swap_summary{output_suffix}.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(summaries.to_string(index=False))
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

