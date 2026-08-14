"""Summarize the frozen Plan-9 architecture-generalization experiment."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats


HERE = Path(__file__).resolve()
P9 = HERE.parents[1]
OUT = P9 / "outputs"
FIG = P9 / "figures"
SEED = 20260814
BOOT = 5000


def rho(a, b):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    keep = np.isfinite(a) & np.isfinite(b)
    if keep.sum() < 4 or np.std(a[keep]) == 0 or np.std(b[keep]) == 0:
        return np.nan
    return float(stats.spearmanr(a[keep], b[keep]).statistic)


def load_data() -> pd.DataFrame:
    new = pd.read_csv(OUT / "p9_disjoint_shared_per_plane.csv")
    old = pd.read_csv(OUT / "p9_disjoint_shared_per_plane_transformer_reference.csv")
    data = pd.concat([old, new], ignore_index=True)
    expected = {"hat", "swinir", "i3net", "saint", "cycleinr"}
    if set(data.model) != expected:
        raise RuntimeError(f"model mismatch: {set(data.model)}")
    if data.groupby(["model", "condition"]).size().ne(120).any():
        raise RuntimeError("each model/condition must have 24 cases x 5 targets")
    return data


def case_table(data: pd.DataFrame) -> pd.DataFrame:
    return (
        data.groupby(["case", "model", "family", "condition"], as_index=False)
        .agg(
            paired_error_mae=("paired_error_mae", "median"),
            disagreement=("prediction_disagreement_mae", "median"),
            error_cosine=("error_cosine", "mean"),
            shared_fraction=("shared_error_fraction", "mean"),
            observable_fraction=("observable_error_fraction", "mean"),
            stable_wrong=("stable_wrong", "mean"),
        )
    )


def effect_rows(cases: pd.DataFrame):
    rng = np.random.default_rng(SEED)
    rows = []
    per_case = []
    for (model, family), g in cases.groupby(["model", "family"]):
        p = g.pivot(index="case", columns="condition")
        ids = p.index.to_numpy()
        obs = p["observable_fraction"]["disjoint"] - p["observable_fraction"]["shared"]
        cos = p["error_cosine"]["shared"] - p["error_cosine"]["disjoint"]
        shr = p["shared_fraction"]["shared"] - p["shared_fraction"]["disjoint"]
        for case in ids:
            per_case.append(
                {
                    "case": case,
                    "model": model,
                    "family": family,
                    "observable_gain": float(obs.loc[case]),
                    "alignment_gain_shared": float(cos.loc[case]),
                    "shared_fraction_gain": float(shr.loc[case]),
                }
            )
        reps = []
        rank_reps = []
        for _ in range(BOOT):
            idx = rng.integers(0, len(ids), len(ids))
            reps.append(float(obs.to_numpy()[idx].mean()))
            es = p["paired_error_mae"]["shared"].to_numpy()[idx]
            ds = p["disagreement"]["shared"].to_numpy()[idx]
            ed = p["paired_error_mae"]["disjoint"].to_numpy()[idx]
            dd = p["disagreement"]["disjoint"].to_numpy()[idx]
            value = rho(ed, dd) - rho(es, ds)
            if np.isfinite(value):
                rank_reps.append(value)
        rank_shared = rho(p["paired_error_mae"]["shared"], p["disagreement"]["shared"])
        rank_disjoint = rho(p["paired_error_mae"]["disjoint"], p["disagreement"]["disjoint"])
        rows.append(
            {
                "dataset": "fastmri",
                "factor": 4,
                "model": model,
                "family": family,
                "cases": len(ids),
                "observable_gain": float(obs.mean()),
                "observable_ci_low": float(np.percentile(reps, 2.5)),
                "observable_ci_high": float(np.percentile(reps, 97.5)),
                "alignment_gain_shared": float(cos.mean()),
                "shared_fraction_gain": float(shr.mean()),
                "ranking_rho_shared": rank_shared,
                "ranking_rho_disjoint": rank_disjoint,
                "ranking_delta": rank_disjoint - rank_shared,
                "ranking_ci_low": float(np.percentile(rank_reps, 2.5)),
                "ranking_ci_high": float(np.percentile(rank_reps, 97.5)),
            }
        )
    return pd.DataFrame(rows), pd.DataFrame(per_case)


def family_meta(per_case: pd.DataFrame):
    family_case = per_case.groupby(["case", "family"], as_index=False).agg(observable_gain=("observable_gain", "mean"))
    matrix = family_case.pivot(index="case", columns="family", values="observable_gain")
    families = list(matrix.columns)
    rng = np.random.default_rng(SEED + 1)
    rows = []
    for removed in [None, *families]:
        keep = [f for f in families if f != removed]
        values = matrix[keep].mean(axis=1).to_numpy()
        reps = []
        for _ in range(BOOT):
            idx = rng.integers(0, len(values), len(values))
            reps.append(float(values[idx].mean()))
        rows.append(
            {
                "analysis": "all_families" if removed is None else f"leave_out_{removed}",
                "families_retained": len(keep),
                "observable_gain": float(values.mean()),
                "ci_low": float(np.percentile(reps, 2.5)),
                "ci_high": float(np.percentile(reps, 97.5)),
                "all_cases_positive": bool(np.all(values > 0)),
            }
        )
    return pd.DataFrame(rows)


def plot_forest(table: pd.DataFrame):
    order = ["hat", "swinir", "i3net", "saint", "cycleinr"]
    labels = {
        "hat": "HAT — Transformer/SR",
        "swinir": "SwinIR — Transformer/SR",
        "i3net": "I3Net — dedicated slice CNN",
        "saint": "SAINT — spatial attention/CNN",
        "cycleinr": "CycleINR-style — implicit coordinate",
    }
    t = table.set_index("model").loc[order].reset_index()
    y = np.arange(len(t))[::-1]
    x = 100 * t.observable_gain.to_numpy()
    lo = 100 * t.observable_ci_low.to_numpy()
    hi = 100 * t.observable_ci_high.to_numpy()
    colors = ["#4c78a8", "#4c78a8", "#f58518", "#54a24b", "#b279a2"]
    fig, ax = plt.subplots(figsize=(8.4, 4.4))
    ax.axvline(0, color="#444444", linewidth=1)
    for xi, yi, li, hii, color in zip(x, y, lo, hi, colors):
        ax.errorbar(xi, yi, xerr=[[xi - li], [hii - xi]], fmt="none", ecolor=color, elinewidth=2, capsize=4)
    ax.scatter(x, y, s=70, c=colors, edgecolor="white", linewidth=0.8, zorder=3)
    ax.set_yticks(y, [labels[m] for m in order])
    ax.set_xlabel("Disjoint − shared observable paired-error fraction (percentage points)")
    ax.set_title("Measurement-disjoint contexts expose more error across architecture families")
    ax.grid(axis="x", alpha=0.2)
    ax.spines[["top", "right"]].set_visible(False)
    for xi, yi in zip(x, y):
        ax.text(xi + 0.7, yi, f"{xi:.1f}", va="center", fontsize=9)
    fig.tight_layout()
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / "p9_architecture_forest.pdf", bbox_inches="tight")
    fig.savefig(FIG / "p9_architecture_forest.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def main():
    data = load_data()
    cases = case_table(data)
    forest, per_case = effect_rows(cases)
    meta = family_meta(per_case)
    forest.to_csv(OUT / "p9_architecture_forest.csv", index=False)
    per_case.to_csv(OUT / "p9_architecture_effect_per_case.csv", index=False)
    meta.to_csv(OUT / "p9_leave_one_family_out.csv", index=False)
    plot_forest(forest)

    new = forest[forest.model.isin(["i3net", "saint", "cycleinr"])]
    verdict = {
        "hypothesis": "H-ARCH-01",
        "new_families_with_positive_observable_gain": int((new.observable_gain > 0).sum()),
        "new_families_total": int(len(new)),
        "new_families_ci_excludes_zero": int((new.observable_ci_low > 0).sum()),
        "ranking_delta_positive": int((new.ranking_delta > 0).sum()),
        "ranking_delta_total": int(len(new)),
        "ranking_delta_ci_excludes_zero": int((new.ranking_ci_low > 0).sum()),
        "mechanism_geometry_verdict": "SUPPORTED_ACROSS_ALL_EVALUATED_NEW_FAMILIES",
        "case_ranking_verdict": "HETEROGENEOUS_CYCLEINR_POSITIVE_I3NET_SMALL_SAINT_NULL_NEGATIVE",
        "claim": "Measurement dependence changes local error alignment and observability across evaluated paradigms; improved examination ranking is not architecture-universal.",
        "falsified_claims": [
            "Every architecture must show a significant disjoint-minus-shared examination-ranking gain.",
            "Architecture breadth alone guarantees useful ranking diversity.",
        ],
        "outputs": [
            "p9_architecture_forest.csv",
            "p9_architecture_effect_per_case.csv",
            "p9_leave_one_family_out.csv",
            "../figures/p9_architecture_forest.pdf",
        ],
    }
    (OUT / "p9_primary_verdict.json").write_text(json.dumps(verdict, indent=2), encoding="utf-8")
    print(forest.to_string(index=False))
    print(meta.to_string(index=False))
    print(json.dumps(verdict, indent=2))


if __name__ == "__main__":
    main()
