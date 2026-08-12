from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .optimization_protocol import ANALYTICAL, FAMILIES, UNIVERSAL_NEURAL


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs" / "nested_optimization"


def main() -> None:
    fidelity = pd.read_csv(OUT / "corrected_reconstruction_fidelity.csv")
    selection = json.loads((OUT / "selected_public_model_bank.json").read_text(encoding="utf-8"))
    summary = (
        fidelity[fidelity.dataset.eq("fastmri")]
        .groupby("model", as_index=False)
        .agg(
            corrected_rank=("corrected_rank", "first"),
            original_unfair_rank=("original_unfair_rank", "first"),
            mean_mae=("mae", "mean"),
            mean_psnr=("psnr", "mean"),
            mean_ssim=("ssim", "mean"),
            mean_ncc=("ncc", "mean"),
        )
    )
    summary["family"] = summary.model.map(FAMILIES)
    summary["kind"] = summary.model.map(lambda value: "analytical" if value in ANALYTICAL else "neural")
    summary["available_fastmri_x2_x4_x6"] = True
    summary["available_ningxia_x2_x4_x6"] = True
    summary["eligible_as_target"] = summary.model.isin(UNIVERSAL_NEURAL)
    summary["main_target"] = summary.model.isin(selection["main_targets"])
    summary["candidate_bank_member"] = summary.model.isin(selection["peer_bank"])
    summary["selection_data"] = "fastMRI x2/x4/x6 common-support development fidelity"
    summary["outer_result_used_for_selection"] = False
    summary = summary.sort_values(["corrected_rank", "model"], na_position="last")
    summary.to_csv(OUT / "model_bank_registry.csv", index=False)

    changed = summary[
        summary.original_unfair_rank.notna()
        & summary.corrected_rank.notna()
        & summary.original_unfair_rank.ne(summary.corrected_rank)
    ]
    changed_text = ", ".join(
        f"{row.model} {int(row.original_unfair_rank)}->{int(row.corrected_rank)}"
        for row in changed.itertuples(index=False)
    ) or "none"
    neural = summary[summary.kind.eq("neural")]
    lines = [
        "# Model Bank Audit",
        "",
        "## Scope",
        "",
        f"- Audited neural reconstructors: {len(neural)}.",
        "- Audited analytical interpolators: Linear and Cubic.",
        "- Availability contract: every listed model has complete finite predictions on fastMRI-brain and NingXia at x2, x4, and x6; NingXia predictions are eight-fold out-of-fold.",
        "- All cross-model fidelity metrics use the same offline ground-truth-derived 1% foreground and generated slices only. This support is never used by deployment scoring.",
        "",
        "## Corrected Selection",
        "",
        f"- Corrected rank changes relative to the old model-specific-mask comparison: {changed_text}.",
        f"- Main targets, fixed before NingXia outer evaluation: {', '.join(selection['main_targets'])}.",
        f"- Candidate peer bank: {', '.join(selection['peer_bank'])}.",
        "- Main-target rule: top half of neural reconstructors by the pre-defined composite rank over common-support MAE, MSE, PSNR, global SSIM, and NCC.",
        "- Peer-bank rule: the six highest-ranked neural peers with at most two members from one architecture family, plus Linear and Cubic.",
        "- Every target is removed from its own committee at scoring time.",
        "",
        "## Terminology and Governance",
        "",
        "The bank is a common-bank, availability-conditioned rule. It is not called a fixed universal committee because target exclusion changes membership and selected subsets may depend on the known interpolation factor and target identity. No NingXia outer-fold error, nAURC, or attribution label was used to define the bank or main targets.",
        "",
        "The machine-readable source is `outputs/nested_optimization/model_bank_registry.csv`.",
    ]
    (ROOT / "MODEL_BANK_AUDIT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    summary.to_csv(ROOT / "model_bank_registry.csv", index=False)


if __name__ == "__main__":
    main()
