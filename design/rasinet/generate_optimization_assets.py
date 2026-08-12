from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs" / "optimization"
PAPER = ROOT / "paper_updated"
TABLES = PAPER / "tables_optimized"
FIGURES = PAPER / "figures_optimized"

ROLES = {
    "c_c98f4ad5b505": "Pre-specified",
    "c_f5fed2ef96c3": "Dev-selected universal",
    "c_a7d0a77ecf68": "Low-cost",
    "c_cc96ad828dc6": "Shared-difficulty",
}


def fmt(value: float, digits: int = 3) -> str:
    return f"{value:.{digits}f}"


def write_validation_table(frame: pd.DataFrame) -> None:
    rows = []
    for (cid, scale), group in frame.groupby(["candidate_id", "scale"], sort=False):
        rows.append(
            (ROLES[cid], int(scale), group["case_spearman"].mean(),
             group["normalized_aurc"].mean(), group["rrr_50"].mean())
        )
    lines = [
        r"\begin{tabular}{llccc}",
        r"\toprule",
        r"Method & Factor & $\rho$ & nAURC$\downarrow$ & RRR50$\uparrow$ \\",
        r"\midrule",
    ]
    last = None
    for role, scale, rho, naurc, rrr in rows:
        if last is not None and role != last:
            lines.append(r"\addlinespace[1.5pt]")
        lines.append(f"{role} & $\\times${scale} & {rho:.3f} & {naurc:.3f} & {100*rrr:.1f}\\% " + r"\\")
        last = role
    lines += [r"\bottomrule", r"\end{tabular}"]
    (TABLES / "table_validation.tex").write_text("\n".join(lines) + "\n", encoding="ascii")


def write_development_table(frame: pd.DataFrame) -> None:
    selected = frame[frame.candidate_id.isin(ROLES)]
    rows = []
    for cid, group in selected.groupby("candidate_id", sort=False):
        rows.append((ROLES[cid], group.normalized_aurc.mean(), group.normalized_aurc.max(),
                     group.case_spearman.mean(), group.rrr_50.mean()))
    lines = [r"\begin{tabular}{lcccc}", r"\toprule",
             r"Method & Mean nAURC & Worst & $\rho$ & RRR50 \\", r"\midrule"]
    for role, mean_n, worst_n, rho, rrr in rows:
        lines.append(f"{role} & {mean_n:.3f} & {worst_n:.3f} & {rho:.3f} & {100*rrr:.1f}\\% " + r"\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    (TABLES / "table_development.tex").write_text("\n".join(lines) + "\n", encoding="ascii")


def plot_transfer(dev: pd.DataFrame, val: pd.DataFrame) -> None:
    order = list(ROLES)
    dev_means = [dev.loc[dev.candidate_id.eq(c), "normalized_aurc"].mean() for c in order]
    val_means = [val.loc[val.candidate_id.eq(c), "normalized_aurc"].mean() for c in order]
    labels = ["Pre-spec.", "Universal", "Low-cost", "Shared"]
    x = np.arange(len(order))
    width = .36
    fig, ax = plt.subplots(figsize=(6.9, 2.25))
    ax.bar(x-width/2, dev_means, width, label="Development", color="#2A6F97")
    ax.bar(x+width/2, val_means, width, label="NingXia validation", color="#D47A36")
    ax.set_ylabel("Mean nAURC (lower is better)")
    ax.set_xticks(x, labels)
    ax.set_ylim(0, max(dev_means + val_means) * 1.22)
    ax.grid(axis="y", color="0.86", linewidth=.6)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, ncol=2, loc="upper left")
    fig.tight_layout(pad=.35)
    fig.savefig(FIGURES / "development_validation_transfer.pdf")
    plt.close(fig)


def write_registry_validation(registry: pd.DataFrame, val: pd.DataFrame) -> None:
    for cid in ROLES:
        mask = registry.candidate_id.eq(cid)
        group = val[val.candidate_id.eq(cid)]
        registry.loc[mask, "validation_status"] = "validated_frozen"
        registry.loc[mask, "mean_validation_nAURC"] = group.normalized_aurc.mean()
        registry.loc[mask, "worst_validation_nAURC"] = group.normalized_aurc.max()
        registry.loc[mask, "mean_validation_rho"] = group.case_spearman.mean()
        registry.loc[mask, "mean_validation_RRR50"] = group.rrr_50.mean()
    registry.to_csv(OUT / "candidate_registry.csv", index=False)


def pareto(frame: pd.DataFrame) -> pd.DataFrame:
    data = frame.copy()
    data["mean_dev_nAURC"] = data.groupby("candidate_id").normalized_aurc.transform("mean")
    data["worst_dev_nAURC"] = data.groupby("candidate_id").normalized_aurc.transform("max")
    compact = data.drop_duplicates("candidate_id")[["candidate_id", "mean_dev_nAURC", "worst_dev_nAURC"]]
    compact["committee_size_proxy"] = compact.candidate_id.map({
        "c_c98f4ad5b505": 4, "c_f5fed2ef96c3": 4,
        "c_a7d0a77ecf68": 3, "c_cc96ad828dc6": 4,
    }).fillna(99)
    vals = compact[["mean_dev_nAURC", "worst_dev_nAURC", "committee_size_proxy"]].to_numpy()
    is_front = []
    for i, row in enumerate(vals):
        dominated = np.any(np.all(vals <= row, axis=1) & np.any(vals < row, axis=1))
        is_front.append(not dominated)
    compact["pareto_front"] = is_front
    compact.to_csv(OUT / "pareto_frontier.csv", index=False)
    return compact


def main() -> None:
    TABLES.mkdir(exist_ok=True)
    FIGURES.mkdir(exist_ok=True)
    dev = pd.read_csv(OUT / "finalist_development_results.csv")
    val = pd.read_csv(OUT / "finalist_validation_results.csv")
    registry = pd.read_csv(OUT / "candidate_registry.csv")
    write_validation_table(val)
    write_development_table(dev)
    plot_transfer(dev, val)
    write_registry_validation(registry, val)
    pareto(dev)
    summary = []
    for cid, role in ROLES.items():
        d = dev[dev.candidate_id.eq(cid)]
        v = val[val.candidate_id.eq(cid)]
        summary.append({"candidate_id": cid, "role": role,
                        "dev_mean_nAURC": d.normalized_aurc.mean(),
                        "dev_worst_nAURC": d.normalized_aurc.max(),
                        "dev_mean_rho": d.case_spearman.mean(),
                        "dev_mean_RRR50": d.rrr_50.mean(),
                        "validation_mean_nAURC": v.normalized_aurc.mean(),
                        "validation_worst_nAURC": v.normalized_aurc.max(),
                        "validation_mean_rho": v.case_spearman.mean(),
                        "validation_mean_RRR50": v.rrr_50.mean()})
    pd.DataFrame(summary).to_csv(OUT / "finalist_summary.csv", index=False)


if __name__ == "__main__":
    main()
