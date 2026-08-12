from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs" / "nested_optimization"
PAPER = ROOT / "paper_updated"
TABLES = PAPER / "tables_nested"
FIGURES = PAPER / "figures_nested"
METHOD_LABELS = {
    "frozen_baseline": "Frozen baseline",
    "nested_triage": "Nested triage",
    "nested_low_cost": "Nested low-cost",
    "mean_disagreement": "Mean disagreement",
    "shared_difficulty": "Shared difficulty",
    "physical_consistency": "Physical consistency",
    "frozen_plus_physical": "Fixed rank hybrid",
    "robust_nested_triage": "Amended nested",
    "robust_nested_low_cost": "Amended low-cost",
}


def fmt(value: float, digits: int = 3) -> str:
    return f"{value:.{digits}f}"


def tex(value: object) -> str:
    return str(value).replace("_", r"\_")


def ci(row: pd.Series, metric: str, digits: int = 3) -> str:
    return f"{fmt(row[metric],digits)} [{fmt(row[metric+'_lo'],digits)}, {fmt(row[metric+'_hi'],digits)}]"


def write_main_table(aggregate: pd.DataFrame) -> None:
    methods = ["frozen_baseline", "physical_consistency", "frozen_plus_physical", "mean_disagreement"]
    rows = []
    for scale in (2, 4, 6):
        for method in methods:
            row = aggregate[(aggregate.level.eq("scale")) & (aggregate.key.astype(str).eq(str(scale))) & aggregate.method.eq(method)].iloc[0]
            rows.append(
                f"$\\times${scale} & {METHOD_LABELS[method]} & {ci(row,'case_spearman')} & "
                f"{ci(row,'normalized_aurc')} & {100*row.rrr_50:.1f}\\% \\\\"
            )
    content = "\n".join([
        "\\begin{tabular}{llccc}",
        "\\toprule",
        "Factor & Method & $\\rho$ [95\\% CI] & nAURC [95\\% CI] & RRR50 \\\\",
        "\\midrule",
        *rows,
        "\\bottomrule",
        "\\end{tabular}",
    ])
    (TABLES / "table_nested_main.tex").write_text(content + "\n", encoding="utf-8")


def write_selection_table(manifest: pd.DataFrame) -> None:
    rows = []
    for role in ("nested_triage", "nested_low_cost"):
        group = manifest[manifest.role.eq(role)]
        for scale in (2, 4, 6):
            g = group[group.scale.eq(scale)]
            neural = g.members.str.split(";").map(lambda values: sum(value not in {"linear", "cubic"} for value in values))
            common_feature = g.feature.mode().iloc[0]
            common_weight = g.weight_mode.mode().iloc[0]
            total = g.members.str.split(";").map(len).mean()
            rows.append(
                f"{METHOD_LABELS[role]} & $\\times${scale} & {neural.mean():.2f} & {total:.2f} & "
                f"{tex(common_feature)} & {tex(common_weight)} " + r"\\"
            )
    content = "\n".join(["\\begin{tabular}{llccll}","\\toprule",
        "Role & Factor & Neural & Total & Modal score & Weight \\\\","\\midrule",*rows,
        "\\bottomrule","\\end{tabular}"])
    (TABLES / "table_nested_selection.tex").write_text(content + "\n", encoding="utf-8")


def write_fidelity_table(fidelity: pd.DataFrame) -> None:
    fidelity = fidelity[fidelity.dataset.eq("fastmri") & fidelity.corrected_rank.notna()]
    overall = fidelity.groupby("model", as_index=False).agg(rank=("corrected_rank","first"),mae=("mae","mean"),
        psnr=("psnr","mean"),ssim=("ssim","mean"),ncc=("ncc","mean"),old=("original_unfair_rank","first")).sort_values("rank")
    rows=[]
    for row in overall.itertuples(index=False):
        old = "--" if not np.isfinite(row.old) else str(int(row.old))
        rows.append(f"{int(row.rank)} & {tex(row.model)} & {row.mae:.2f} & {row.psnr:.2f} & {row.ssim:.3f} & {row.ncc:.3f} & {old} " + r"\\")
    content="\n".join(["\\begin{tabular}{r l r r r r r}","\\toprule","Rank & Model & MAE & PSNR & SSIM & NCC & Old rank \\\\","\\midrule",*rows,"\\bottomrule","\\end{tabular}"])
    (TABLES/"table_corrected_fidelity.tex").write_text(content+"\n",encoding="utf-8")
    compact=[]
    for row in overall.head(6).itertuples(index=False):
        old="--" if not np.isfinite(row.old) else str(int(row.old))
        compact.append(f"{int(row.rank)} & {tex(row.model)} & {row.mae:.1f} & {row.ssim:.3f} & {old} " + r"\\")
    compact_content="\n".join(["\\begin{tabular}{r l r r r}","\\toprule","Rank & Model & MAE & SSIM & Old \\\\","\\midrule",*compact,"\\bottomrule","\\end{tabular}"])
    (TABLES/"table_fidelity_regular.tex").write_text(compact_content+"\n",encoding="utf-8")


def write_adaptive_table(aggregate: pd.DataFrame, manifest: pd.DataFrame) -> None:
    robust_manifest=pd.read_csv(OUT/"ningxia_robust_selection_manifest.csv")
    neural={
        "nested_triage":manifest[manifest.role.eq("nested_triage")].members.str.split(";").map(lambda v:sum(x not in {"linear","cubic"} for x in v)).mean(),
        "robust_nested_triage":robust_manifest[robust_manifest.role.eq("robust_nested_triage")].members.str.split(";").map(lambda v:sum(x not in {"linear","cubic"} for x in v)).mean(),
    }
    labels={"frozen_baseline":"Frozen baseline","physical_consistency":"Physical consistency",
            "nested_triage":"Unconstrained nested","robust_nested_triage":"Amended nested"}
    rows=[]
    for method in labels:
        row=aggregate[(aggregate.level.eq("overall"))&aggregate.method.eq(method)].iloc[0]
        peers="--" if method not in neural else f"{neural[method]:.2f}"
        rows.append(f"{labels[method]} & {row.case_spearman:.3f} & {row.normalized_aurc:.3f} & {100*row.rrr_50:.1f}\\% & {peers} " + r"\\")
    content="\n".join(["\\begin{tabular}{lrrrr}","\\toprule","Method & $\\rho$ & nAURC & RRR50 & Neural peers \\\\","\\midrule",*rows,"\\bottomrule","\\end{tabular}"])
    (TABLES/"table_adaptive_regular.tex").write_text(content+"\n",encoding="utf-8")


def write_attribution_table(attr: pd.DataFrame) -> None:
    main=attr[attr.role.eq("nested_attribution")]
    rows=[f"$\\times${int(r.scale)} & {r.matched_advantage:.3f} & {r.within_case_spearman:.3f} & {100*r.top1_accuracy:.1f}\\% & {r.pooled_relative_correlation:.3f} " + r"\\" for r in main.itertuples(index=False)]
    content="\n".join(["\\begin{tabular}{lrrrr}","\\toprule","Factor & Match adv. & Within-case $\\rho$ & Top-1 & Pooled $\\rho$ \\\\","\\midrule",*rows,"\\bottomrule","\\end{tabular}"])
    (TABLES/"table_nested_attribution.tex").write_text(content+"\n",encoding="utf-8")


def write_transfer_table(transfer: pd.DataFrame) -> None:
    rows=[]
    grouped=transfer.groupby(["analysis","selection_scales","test_dataset","test_scale"],as_index=False).agg(
        profiles=("target_model","nunique"),rho=("case_spearman","mean"),naurc=("normalized_aurc","mean"),rrr=("rrr_50","mean"))
    for row in grouped.itertuples(index=False):
        label=tex(row.analysis.replace("_retrospective",""))
        rows.append(f"{label} & {row.selection_scales} & {tex(row.test_dataset)} $\\times${int(row.test_scale)} & {int(row.profiles)} & {row.rho:.3f} & {row.naurc:.3f} & {100*row.rrr:.1f}\\% " + r"\\")
    content="\n".join(["\\begin{tabular}{lllrrrr}","\\toprule","Analysis & Select factors & Test profile & Targets & $\\rho$ & nAURC & RRR50 \\\\","\\midrule",*rows,"\\bottomrule","\\end{tabular}"])
    (TABLES/"table_transfer.tex").write_text(content+"\n",encoding="utf-8")


def make_figure(aggregate: pd.DataFrame, attr: pd.DataFrame, physical: pd.DataFrame) -> None:
    plt.rcParams.update({"font.size": 8, "font.family": "DejaVu Sans", "pdf.fonttype": 42, "ps.fonttype": 42})
    fig, axes = plt.subplots(1, 3, figsize=(7.1, 2.15))
    methods=["frozen_baseline","physical_consistency","frozen_plus_physical"]
    colors=["#4d4d4d","#0072B2","#D55E00"]
    x=np.arange(3); width=.23
    for offset,(method,color) in enumerate(zip(methods,colors)):
        values=[]; low=[]; high=[]
        for scale in (2,4,6):
            row=aggregate[(aggregate.level.eq("scale"))&(aggregate.key.astype(str).eq(str(scale)))&aggregate.method.eq(method)].iloc[0]
            values.append(row.normalized_aurc); low.append(row.normalized_aurc-row.normalized_aurc_lo); high.append(row.normalized_aurc_hi-row.normalized_aurc)
        axes[0].bar(x+(offset-1)*width,values,width,color=color,label=METHOD_LABELS[method],yerr=[low,high],capsize=2)
    axes[0].set_xticks(x,["x2","x4","x6"]); axes[0].set_ylabel("nAURC (lower better)"); axes[0].set_title("A. Nested outer-fold triage")
    axes[0].grid(axis="y",alpha=.22); axes[0].legend(fontsize=6,frameon=False)

    main=attr[attr.role.eq("nested_attribution")].sort_values("scale")
    axes[1].plot(main.scale,main.within_case_spearman,"o-",color="#009E73",label="within-case rho")
    axes[1].plot(main.scale,main.matched_advantage,"s--",color="#CC79A7",label="matched advantage")
    axes[1].axhline(0,color="0.6",lw=.8); axes[1].set_xticks([2,4,6],["x2","x4","x6"])
    axes[1].set_title("B. Target attribution"); axes[1].grid(axis="y",alpha=.22); axes[1].legend(fontsize=6,frameon=False)

    p=physical[(physical.dataset.eq("ningxia"))].groupby(["scale","method"],as_index=False).normalized_aurc.mean()
    for method,style,color in (("physical_consistency","o--","#56B4E9"),("frozen_disagreement_plus_physical_rank","s-","#E69F00")):
        g=p[p.method.eq(method)].sort_values("scale")
        axes[2].plot(g.scale,g.normalized_aurc,style,color=color,label=method.replace("_"," "))
    axes[2].set_xticks([2,4,6],["x2","x4","x6"]); axes[2].set_title("C. Physical cross-scale signal")
    axes[2].set_ylabel("nAURC"); axes[2].grid(axis="y",alpha=.22); axes[2].legend(fontsize=5.7,frameon=False)
    fig.tight_layout(pad=.7,w_pad=.7); fig.savefig(FIGURES/"nested_multiscale_results.pdf",bbox_inches="tight"); fig.savefig(FIGURES/"nested_multiscale_results.png",dpi=250,bbox_inches="tight"); plt.close(fig)


def write_macros(aggregate: pd.DataFrame, paired: pd.DataFrame, attr: pd.DataFrame,
                 interaction: pd.DataFrame, manifest: pd.DataFrame, physical_pairs: pd.DataFrame) -> None:
    def overall(method: str) -> pd.Series:
        return aggregate[(aggregate.level.eq("overall"))&aggregate.method.eq(method)].iloc[0]
    baseline=overall("frozen_baseline"); triage=overall("physical_consistency"); low=overall("frozen_plus_physical")
    delta=paired[(paired.level.eq("overall"))&(paired.key.eq("all"))&(paired.method.eq("physical_consistency"))&(paired.comparator.eq("frozen_baseline"))].iloc[0]
    attr_mean=attr[attr.role.eq("nested_attribution")].mean(numeric_only=True)
    nested_members=manifest[manifest.role.eq("nested_triage")].members.str.split(";")
    low_members=manifest[manifest.role.eq("nested_low_cost")].members.str.split(";")
    macros={
        "NestedInteractionCount":f"{len(interaction):,}",
        "NestedRetainedCount":f"{int(interaction.selected_for_nested.astype(str).str.lower().eq('true').sum()):,}",
        "NestedBaselineNAURC":fmt(baseline.normalized_aurc),"NestedTriageNAURC":fmt(triage.normalized_aurc),"NestedLowNAURC":fmt(low.normalized_aurc),
        "NestedBaselineRho":fmt(baseline.case_spearman),"NestedTriageRho":fmt(triage.case_spearman),"NestedLowRho":fmt(low.case_spearman),
        "NestedBaselineRRR":f"{100*baseline.rrr_50:.1f}\\%","NestedTriageRRR":f"{100*triage.rrr_50:.1f}\\%","NestedLowRRR":f"{100*low.rrr_50:.1f}\\%",
        "NestedDeltaNAURC":fmt(delta.delta_normalized_aurc),"NestedDeltaNAURCLo":fmt(delta.delta_normalized_aurc_lo),"NestedDeltaNAURCHi":fmt(delta.delta_normalized_aurc_hi),
        "NestedAttrAdv":fmt(attr_mean.matched_advantage),"NestedAttrWithin":fmt(attr_mean.within_case_spearman),"NestedAttrTop":f"{100*attr_mean.top1_accuracy:.1f}\\%",
        "NestedMeanNeural":f"{nested_members.map(lambda v:sum(x not in {'linear','cubic'} for x in v)).mean():.2f}",
        "NestedLowMeanNeural":f"{low_members.map(lambda v:sum(x not in {'linear','cubic'} for x in v)).mean():.2f}",
        "PhysicalMatchedRecords":f"{int(physical_pairs.status.eq('matched_physical_planes').sum()):,}",
    }
    (TABLES/"nested_macros.tex").write_text("\n".join(f"\\newcommand{{\\{key}}}{{{value}}}" for key,value in macros.items())+"\n",encoding="utf-8")
    trace=[
        {"claim":"overall frozen baseline nAURC","macro":"NestedBaselineNAURC","source":"nested_aggregate_results.csv","filter":"level=overall,key=all,method=frozen_baseline"},
        {"claim":"overall physical consistency nAURC","macro":"NestedTriageNAURC","source":"nested_aggregate_results.csv","filter":"level=overall,key=all,method=physical_consistency"},
        {"claim":"paired aggregate delta nAURC","macro":"NestedDeltaNAURC","source":"profile_aligned_paired_summary.csv","filter":"overall physical_consistency-frozen_baseline"},
        {"claim":"target attribution","macro":"NestedAttrAdv/NestedAttrWithin/NestedAttrTop","source":"target_attribution_nested_results.csv","filter":"role=nested_attribution"},
        {"claim":"physical matching feasible","macro":"PhysicalMatchedRecords","source":"cross_scale_physical_pair_scores.csv","filter":"status=matched_physical_planes"},
    ]
    pd.DataFrame(trace).to_csv(OUT/"nested_claim_traceability.csv",index=False)


def main() -> None:
    TABLES.mkdir(parents=True,exist_ok=True); FIGURES.mkdir(parents=True,exist_ok=True)
    aggregate=pd.read_csv(OUT/"nested_aggregate_results.csv")
    paired=pd.read_csv(OUT/"profile_aligned_paired_summary.csv")
    attr=pd.read_csv(OUT/"target_attribution_nested_results.csv")
    interaction=pd.read_csv(OUT/"score_committee_interaction_results.csv")
    manifest=pd.read_csv(OUT/"ningxia_nested_selection_manifest.csv")
    physical=pd.read_csv(OUT/"cross_scale_consistency_results.csv")
    physical_pairs=pd.read_csv(OUT/"cross_scale_physical_pair_scores.csv")
    fidelity=pd.read_csv(OUT/"corrected_reconstruction_fidelity.csv")
    write_main_table(aggregate); write_selection_table(manifest); write_fidelity_table(fidelity); write_adaptive_table(aggregate,manifest); write_attribution_table(attr)
    if (OUT/"frozen_transfer_results.csv").exists():
        write_transfer_table(pd.read_csv(OUT/"frozen_transfer_results.csv"))
    make_figure(aggregate,attr,physical); write_macros(aggregate,paired,attr,interaction,manifest,physical_pairs)
    print(f"paper assets: {TABLES} and {FIGURES}")


if __name__ == "__main__":
    main()
