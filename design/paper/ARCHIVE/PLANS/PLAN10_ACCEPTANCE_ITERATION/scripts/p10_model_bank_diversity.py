"""Exploratory breadth audit of case-error dependence and pair reliability.

All outputs are derived from frozen, common-support per-case tables.  The script
does not train models, load protected image volumes, or alter upstream results.
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats


HERE = Path(__file__).resolve()
P10 = HERE.parents[1]
PAPER = P10.parent
ROOT = PAPER.parents[1]
OUT = P10 / "outputs"
FIG = P10 / "figures"
SEED = 20260827
BOOTSTRAPS = 500


def rho(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    keep = np.isfinite(a) & np.isfinite(b)
    if keep.sum() < 5 or np.std(a[keep]) == 0 or np.std(b[keep]) == 0:
        return np.nan
    return float(stats.spearmanr(a[keep], b[keep]).statistic)


def load_inputs():
    nested = ROOT / "design" / "rasinet" / "outputs" / "nested_optimization"
    fidelity = pd.concat(
        [
            pd.read_csv(nested / "common_fidelity_per_case_development.csv"),
            pd.read_csv(nested / "common_fidelity_per_case_ningxia.csv"),
        ],
        ignore_index=True,
    )
    pair_features = pd.concat(
        [
            pd.read_csv(nested / "pair_features_per_case_development.csv"),
            pd.read_csv(nested / "pair_features_per_case_ningxia.csv"),
        ],
        ignore_index=True,
    )
    registry = pd.read_csv(ROOT / "design" / "rasinet" / "model_bank_registry.csv")
    families = dict(zip(registry.model, registry.family))
    families["acsinet"] = "attention_cnn"
    return fidelity, pair_features, families


def pair_error_dependence(fidelity, families):
    rows = []
    for (dataset, factor), group in fidelity.groupby(["dataset", "scale"]):
        pivot = group.pivot(index="case", columns="model", values="mae")
        for model_a, model_b in itertools.combinations(sorted(pivot.columns), 2):
            pair = pivot[[model_a, model_b]].dropna()
            top_a = set(pair.index[pair[model_a] >= pair[model_a].quantile(0.75)])
            top_b = set(pair.index[pair[model_b] >= pair[model_b].quantile(0.75)])
            rows.append(
                {
                    "dataset": dataset,
                    "factor": int(factor),
                    "model_a": model_a,
                    "model_b": model_b,
                    "family_a": families[model_a],
                    "family_b": families[model_b],
                    "same_family": families[model_a] == families[model_b],
                    "n_cases": len(pair),
                    "error_rank_rho": rho(pair[model_a], pair[model_b]),
                    "top_quartile_jaccard": len(top_a & top_b) / max(len(top_a | top_b), 1),
                }
            )
    return pd.DataFrame(rows)


def directed_reliability(fidelity, pair_features, families, error_pairs):
    rows = []
    error_lookup = {}
    for row in error_pairs.itertuples():
        error_lookup[(row.dataset, row.factor, frozenset((row.model_a, row.model_b)))] = row.error_rank_rho
    mae = fidelity[["dataset", "scale", "case", "model", "mae"]]
    for (dataset, factor, target, member), group in pair_features.groupby(
        ["dataset", "scale", "target_model", "member"]
    ):
        target_mae = mae[
            (mae.dataset == dataset) & (mae.scale == factor) & (mae.model == target)
        ][["case", "mae"]]
        merged = group[["fold", "case", "intensity_mean__target_0.01"]].merge(
            target_mae, on="case", how="inner"
        )
        if len(merged) < 8:
            continue
        rows.append(
            {
                "dataset": dataset,
                "factor": int(factor),
                "target_model": target,
                "member": member,
                "target_family": families[target],
                "member_family": families[member],
                "same_family": families[target] == families[member],
                "n_cases": len(merged),
                "error_rank_rho": error_lookup.get(
                    (dataset, int(factor), frozenset((target, member))), np.nan
                ),
                "disagreement_error_rho": rho(
                    merged["intensity_mean__target_0.01"], merged["mae"]
                ),
            }
        )
    return pd.DataFrame(rows)


def matched_family_contrasts(directed):
    rows = []
    for (dataset, factor, target), group in directed.groupby(
        ["dataset", "factor", "target_model"]
    ):
        same = group[group.same_family].disagreement_error_rho.dropna()
        cross = group[~group.same_family].disagreement_error_rho.dropna()
        if same.empty or cross.empty:
            continue
        rows.append(
            {
                "dataset": dataset,
                "factor": int(factor),
                "target_model": target,
                "target_family": group.target_family.iloc[0],
                "same_family_members": int(len(same)),
                "cross_family_members": int(len(cross)),
                "same_family_median_rho": float(same.median()),
                "cross_family_median_rho": float(cross.median()),
                "cross_minus_same_rho": float(cross.median() - same.median()),
                "best_member": group.loc[group.disagreement_error_rho.idxmax(), "member"],
                "best_member_rho": float(group.disagreement_error_rho.max()),
            }
        )
    return pd.DataFrame(rows)


def summarize(error_pairs, directed, contrasts):
    rows = []
    keys = sorted(set(zip(error_pairs.dataset, error_pairs.factor)))
    for dataset, factor in keys:
        ep = error_pairs[(error_pairs.dataset == dataset) & (error_pairs.factor == factor)]
        dr = directed[(directed.dataset == dataset) & (directed.factor == factor)]
        ct = contrasts[(contrasts.dataset == dataset) & (contrasts.factor == factor)]
        assoc = rho(dr.error_rank_rho, dr.disagreement_error_rho)
        rows.append(
            {
                "dataset": dataset,
                "factor": int(factor),
                "models": int(len(set(ep.model_a) | set(ep.model_b))),
                "undirected_pairs": len(ep),
                "median_error_rank_rho": ep.error_rank_rho.median(),
                "q10_error_rank_rho": ep.error_rank_rho.quantile(0.10),
                "minimum_error_rank_rho": ep.error_rank_rho.min(),
                "fraction_error_rho_gt_0.9": float((ep.error_rank_rho > 0.9).mean()),
                "median_top_quartile_jaccard": ep.top_quartile_jaccard.median(),
                "directed_pairs": len(dr),
                "median_disagreement_error_rho": dr.disagreement_error_rho.median(),
                "q10_disagreement_error_rho": dr.disagreement_error_rho.quantile(0.10),
                "error_dependence_vs_reliability_rho": assoc,
                "matched_targets": len(ct),
                "median_cross_minus_same_rho": ct.cross_minus_same_rho.median()
                if len(ct)
                else np.nan,
                "positive_cross_minus_same": int((ct.cross_minus_same_rho > 0).sum()),
            }
        )
    return pd.DataFrame(rows)


def clustered_bootstrap(fidelity, pair_features, families, summary):
    rng = np.random.default_rng(SEED)
    records = []
    for base in summary.itertuples():
        f = fidelity[(fidelity.dataset == base.dataset) & (fidelity.scale == base.factor)].copy()
        p = pair_features[
            (pair_features.dataset == base.dataset) & (pair_features.scale == base.factor)
        ].copy()
        if base.dataset == "ningxia":
            unit_by_case = f[["case", "fold"]].drop_duplicates().set_index("case")["fold"].to_dict()
        else:
            unit_by_case = {case: case for case in f.case.unique()}
        units = np.array(sorted(set(unit_by_case.values())), dtype=object)
        cases_by_unit = {
            unit: sorted([case for case, mapped in unit_by_case.items() if mapped == unit])
            for unit in units
        }
        fwide = f.pivot(index="case", columns="model", values="mae")
        models = list(fwide.columns)
        pair_index = list(itertools.combinations(range(len(models)), 2))
        pair_tables = {}
        for (target, member), g in p.groupby(["target_model", "member"]):
            pair_tables[(target, member)] = g.set_index("case")["intensity_mean__target_0.01"]
        target_family_options = {}
        for target in sorted(p.target_model.unique()):
            members = sorted(p[p.target_model == target].member.unique())
            same = [m for m in members if families[m] == families[target]]
            cross = [m for m in members if families[m] != families[target]]
            if same and cross:
                target_family_options[target] = (same, cross)
        for b in range(BOOTSTRAPS):
            sampled_units = rng.choice(units, size=len(units), replace=True)
            sampled_cases = []
            for rep, unit in enumerate(sampled_units):
                sampled_cases.extend(cases_by_unit[unit])
            matrix = fwide.loc[sampled_cases].to_numpy(dtype=float)
            corr = stats.spearmanr(matrix, axis=0).statistic
            if np.ndim(corr) == 0:
                continue
            pair_rhos = np.array([corr[i, j] for i, j in pair_index], dtype=float)
            directed_rhos = []
            target_contrasts = []
            per_target = {}
            for (target, member), scores in pair_tables.items():
                if target not in fwide.columns:
                    continue
                target_values = fwide.loc[sampled_cases, target].to_numpy(dtype=float)
                score_values = scores.loc[sampled_cases].to_numpy(dtype=float)
                value = rho(score_values, target_values)
                directed_rhos.append(value)
                per_target[(target, member)] = value
            for target, (same_members, cross_members) in target_family_options.items():
                same_vals = [per_target[(target, m)] for m in same_members]
                cross_vals = [per_target[(target, m)] for m in cross_members]
                target_contrasts.append(np.nanmedian(cross_vals) - np.nanmedian(same_vals))
            records.append(
                {
                    "dataset": base.dataset,
                    "factor": int(base.factor),
                    "bootstrap": b,
                    "median_error_rank_rho": np.nanmedian(pair_rhos),
                    "median_disagreement_error_rho": np.nanmedian(directed_rhos),
                    "median_cross_minus_same_rho": np.nanmedian(target_contrasts)
                    if target_contrasts
                    else np.nan,
                }
            )
    draws = pd.DataFrame(records)
    ci_rows = []
    for (dataset, factor), group in draws.groupby(["dataset", "factor"]):
        row = {"dataset": dataset, "factor": int(factor), "bootstraps": len(group)}
        for metric in [
            "median_error_rank_rho",
            "median_disagreement_error_rho",
            "median_cross_minus_same_rho",
        ]:
            values = group[metric].dropna()
            row[f"{metric}_lo"] = values.quantile(0.025)
            row[f"{metric}_hi"] = values.quantile(0.975)
        ci_rows.append(row)
    return draws, pd.DataFrame(ci_rows)


def make_figure(error_pairs, directed, contrasts, summary, ci):
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8.5,
            "axes.titlesize": 9.5,
            "axes.labelsize": 8.5,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
    labels = [f"{r.dataset}\n×{int(r.factor)}" for r in summary.itertuples()]
    colors = {"fastmri": "#277DA1", "ixi": "#43AA8B", "ningxia": "#F8961E"}
    fig, axes = plt.subplots(1, 3, figsize=(11.6, 3.25), constrained_layout=True)

    ax = axes[0]
    for xpos, row in enumerate(summary.itertuples()):
        group = error_pairs[(error_pairs.dataset == row.dataset) & (error_pairs.factor == row.factor)]
        cross = group[~group.same_family].error_rank_rho
        same = group[group.same_family].error_rank_rho
        jitter = np.linspace(-0.11, 0.11, len(cross)) if len(cross) else []
        ax.scatter(
            xpos + jitter,
            cross,
            s=7,
            alpha=0.24,
            color=colors[row.dataset],
            edgecolors="none",
        )
        ax.scatter(
            np.full(len(same), xpos),
            same,
            s=23,
            marker="D",
            facecolor="white",
            edgecolor="#222222",
            linewidth=0.7,
            zorder=4,
        )
        ax.plot([xpos - 0.20, xpos + 0.20], [group.error_rank_rho.median()] * 2, color="#111111", lw=1.2)
    ax.axhline(0.9, color="#777777", ls="--", lw=0.8)
    ax.set_xticks(range(len(labels)), labels)
    ax.set_ylim(0.25, 1.015)
    ax.set_ylabel("Pairwise case-error rank $\\rho$")
    ax.set_title("(a) Common case difficulty persists")
    ax.text(0.02, 0.03, "diamonds: same family", transform=ax.transAxes, fontsize=7.2)

    ax = axes[1]
    for row in directed.itertuples():
        marker = "D" if row.same_family else "o"
        ax.scatter(
            row.error_rank_rho,
            row.disagreement_error_rho,
            s=15 if row.same_family else 8,
            marker=marker,
            facecolor="white" if row.same_family else colors[row.dataset],
            edgecolor="#222222" if row.same_family else "none",
            linewidth=0.55,
            alpha=0.72,
        )
    ax.set_xlim(0.25, 1.01)
    ax.set_ylim(0.0, 1.01)
    ax.set_xlabel("Target--member error-rank $\\rho$")
    ax.set_ylabel("Disagreement--target-error $\\rho$")
    ax.set_title("(b) Dependence does not determine reliability")

    ax = axes[2]
    target_colors = {"transformer": "#577590", "implicit": "#F94144", "attention_cnn": "#90BE6D"}
    for i, row in enumerate(contrasts.sort_values(["target_family", "dataset", "factor"]).itertuples()):
        x = {"transformer": 0, "implicit": 1, "attention_cnn": 2}.get(row.target_family, 3)
        offset = ((i % 7) - 3) * 0.035
        ax.scatter(
            x + offset,
            row.cross_minus_same_rho,
            s=22,
            color=colors[row.dataset],
            edgecolor="#222222",
            linewidth=0.35,
            alpha=0.85,
        )
    ax.axhline(0, color="#555555", lw=0.9)
    ax.set_xticks([0, 1, 2], ["Transformer", "Implicit", "Attention CNN"])
    ax.set_ylabel("Cross-family median $\\rho$ minus same-family $\\rho$")
    ax.set_title("(c) Family effect is target dependent")
    ax.text(0.02, 0.03, "positive favors cross-family partner", transform=ax.transAxes, fontsize=7.2)

    fig.suptitle(
        "Recovered-model-bank audit: architecture labels do not guarantee independent or more useful errors",
        fontsize=10.2,
        fontweight="bold",
    )
    for suffix in ["pdf", "png"]:
        fig.savefig(FIG / f"p10_model_bank_diversity.{suffix}", dpi=300, bbox_inches="tight")
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    fidelity, pair_features, families = load_inputs()
    error_pairs = pair_error_dependence(fidelity, families)
    directed = directed_reliability(fidelity, pair_features, families, error_pairs)
    contrasts = matched_family_contrasts(directed)
    summary = summarize(error_pairs, directed, contrasts)
    draws, ci = clustered_bootstrap(fidelity, pair_features, families, summary)
    error_pairs.to_csv(OUT / "p10_all_method_pair_error_dependence.csv", index=False)
    directed.to_csv(OUT / "p10_directed_disagreement_reliability.csv", index=False)
    contrasts.to_csv(OUT / "p10_target_matched_family_contrast.csv", index=False)
    summary.to_csv(OUT / "p10_stratum_summary.csv", index=False)
    draws.to_csv(OUT / "p10_cluster_bootstrap_draws.csv", index=False)
    ci.to_csv(OUT / "p10_cluster_bootstrap_ci.csv", index=False)
    make_figure(error_pairs, directed, contrasts, summary, ci)
    verdict = {
        "status": "exploratory_breadth_audit",
        "seed": SEED,
        "bootstraps": BOOTSTRAPS,
        "strata": len(summary),
        "error_pairs": len(error_pairs),
        "directed_pairs": len(directed),
        "matched_targets": len(contrasts),
        "all_stratum_median_error_rho_gt_0_9": bool((summary.median_error_rank_rho > 0.9).all()),
        "family_contrast_has_both_signs": bool(
            (contrasts.cross_minus_same_rho > 0).any()
            and (contrasts.cross_minus_same_rho < 0).any()
        ),
        "interpretation": (
            "Case difficulty is broadly shared, while cross-family pairing has target-family- and "
            "cohort-dependent value; architecture family is not a universal proxy for useful error independence."
        ),
    }
    (OUT / "p10_verdict.json").write_text(json.dumps(verdict, indent=2), encoding="utf-8")
    print(json.dumps(verdict, indent=2))


if __name__ == "__main__":
    main()
