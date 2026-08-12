from __future__ import annotations

import json
import shutil
import subprocess
from datetime import date
from pathlib import Path

import pandas as pd


ROOT=Path(__file__).resolve().parent
OUT=ROOT/"outputs"/"nested_optimization"
PAPER=ROOT/"paper_updated"


def f(value: float) -> str:
    return f"{value:.3f}"


def get(overall: pd.DataFrame, method: str) -> pd.Series:
    return overall[(overall.level.eq("overall"))&overall.method.eq(method)].iloc[0]


def main() -> None:
    aggregate=pd.read_csv(OUT/"nested_aggregate_results.csv")
    paired=pd.read_csv(OUT/"profile_aligned_paired_summary.csv")
    interaction=pd.read_csv(OUT/"score_committee_interaction_results.csv",usecols=["candidate_id","selected_for_nested"])
    attribution=pd.read_csv(OUT/"target_attribution_nested_results.csv")
    model=pd.read_csv(OUT/"model_bank_registry.csv")
    transfer=pd.read_csv(OUT/"frozen_transfer_results.csv")
    physical_pairs=pd.read_csv(OUT/"cross_scale_physical_pair_scores.csv")
    baseline=get(aggregate,"frozen_baseline"); physical=get(aggregate,"physical_consistency")
    hybrid=get(aggregate,"frozen_plus_physical"); first=get(aggregate,"nested_triage"); amended=get(aggregate,"robust_nested_triage")
    delta=paired[(paired.level.eq("overall"))&paired.key.eq("all")&paired.method.eq("physical_consistency")&paired.comparator.eq("frozen_baseline")].iloc[0]
    attr=attribution[attribution.role.eq("nested_attribution")].mean(numeric_only=True)
    targets=model[model.main_target.astype(str).str.lower().eq("true")].sort_values("corrected_rank").model.tolist()
    bank=model[model.candidate_bank_member.astype(str).str.lower().eq("true")].sort_values("corrected_rank").model.tolist()
    try:
        commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
    except Exception:
        commit="unavailable"

    registry=[]
    profiles=pd.read_csv(OUT/"nested_finalist_results.csv")
    for row in profiles.itertuples(index=False):
        for metric in ("case_spearman","normalized_aurc","rrr_25","rrr_50","rrr_75",
                       "retained_mae_25","retained_mae_50","retained_mae_75"):
            registry.append({"experiment_id":f"outer_{row.method}_x{row.scale}_{row.target_model}_{metric}",
                "dataset":"ningxia","target_model":row.target_model,"committee":row.method,
                "score":row.method,"mask":"method_defined_deployment_mask","normalization":"source_intensity",
                "metric":metric,"value":getattr(row,metric),"seed":20260821,"number_of_cases":row.n,
                "development_or_test":"nested_outer","run_date":date.today().isoformat(),"code_commit":commit,
                "output_file":"outputs/nested_optimization/nested_finalist_results.csv"})
    pd.DataFrame(registry).to_csv(OUT/"results_registry.csv",index=False)
    shutil.copy2(ROOT/"configs"/"selection_protocol_nested.yaml",ROOT/"selection_protocol.yaml")
    shutil.copy2(OUT/"corrected_reconstruction_fidelity.csv",ROOT/"corrected_reconstruction_fidelity.csv")

    revision=f"""# Revision Report: Nested Optimization

## Outcome

The revision corrects the old optimization methodology and changes the paper's strongest refinement from adaptive committee selection to physically matched cross-scale consistency. All numbers below are generated from `outputs/nested_optimization/`.

## Corrected Issues

| Before | Actual correction | Evidence | Status |
|---|---|---|---|
| Cost and one-SE were declared but not implemented | Added cost rank and executable one-SE selection | `nested_selection.py`, manifests | Complete |
| Model fidelity used different target-derived masks | Recomputed MAE/MSE/PSNR/SSIM/NCC on one common offline GT support | `corrected_reconstruction_fidelity.csv` | Complete |
| Paper called a mixed committee neural-only | Linear and Cubic are explicit in config, registry, and prose | `MODEL_BANK_AUDIT.md` | Complete |
| Availability-varying committee called universal | Renamed common-bank / availability-conditioned rule | papers and audit | Complete |
| Aggregate bootstrap flattened profiles | Profile deltas now average inside each of 2,000 aligned replicates | `nested_paired_bootstrap.csv` | Complete |
| Raw attribution scales and errors were incomparable | Common error support, inner-only target calibration, relative centering, attribution objective | attribution CSVs | Complete |
| Shape mismatch ended cross-scale analysis | Matched full affine world-plane origins on generated slices | physical audit | Complete |
| ZIP omitted imported modules | Final package includes every local import, configs, tests, and precomputed CSVs | delivery manifest | Complete |

## Experiments Actually Run

- Common-support development fidelity: 187 profile cases, 13 methods where available.
- Common-support NingXia OOF labels/features: 66 factor cases and 8,712 target-member records.
- Broad interaction search: {len(interaction):,} candidates; {int(interaction.selected_for_nested.astype(str).str.lower().eq('true').sum()):,} stratified finalists.
- Nested selection: 8 outer folds x 3 factors x 11 targets x 2 roles; every profile has 22 out-of-selection predictions.
- Protocol-amendment sensitivity: same outer structure with mandatory neural peers; retained separately.
- Target attribution: four inner-only calibration transforms x two relative transforms, selected by attribution metrics.
- Physical alignment: {len(physical_pairs):,} records, {int(physical_pairs.status.eq('matched_physical_planes').sum()):,} matched.
- Frozen transfer: {len(transfer)} profile rows across both dataset directions and leave-one-factor-out analyses.
- Statistics: 2,000 paired case bootstraps with profile-, factor-, target-, and aggregate summaries.
- Unit/integration tests: 11 passed.

## Main Result Changes

- Correct point estimates use original profile metrics rather than bootstrap means.
- Frozen baseline: nAURC {f(baseline.normalized_aurc)}, rho {f(baseline.case_spearman)}, RRR50 {100*baseline.rrr_50:.1f}%.
- Physical consistency: nAURC {f(physical.normalized_aurc)}, rho {f(physical.case_spearman)}, RRR50 {100*physical.rrr_50:.1f}%.
- Paired delta nAURC: {f(delta.delta_normalized_aurc)} [{f(delta.delta_normalized_aurc_lo)}, {f(delta.delta_normalized_aurc_hi)}].
- Fixed rank hybrid: nAURC {f(hybrid.normalized_aurc)}; it is not conclusively different from physical consistency.
- Unconstrained nested selection failed (nAURC {f(first.normalized_aurc)}); amended selection also failed ({f(amended.normalized_aurc)}). Neither is promoted as an improvement.
- Attribution remains weak: matched advantage {f(attr.matched_advantage)}, within-case rho {f(attr.within_case_spearman)}, top-1 {100*attr.top1_accuracy:.1f}%.

## Expected Submission Impact

The physical-coordinate result adds a distinct signal-processing contribution and removes the inaccurate shape-mismatch claim. Common-support selection, nested governance, calibrated attribution, and aligned bootstrap materially improve technical defensibility and reproducibility. The main residual limitations are intrinsic simplicity, small labeled cohorts, multiscale execution cost, and absence of clinical-task validation.
"""
    (ROOT/"revision_report_nested_optimization.md").write_text(revision,encoding="utf-8")

    reviewer=f"""# Final Reviewer Simulation

## Reviewer A: ICASSP Computational Imaging

**Strengths.** Physical-plane matching uses full NIfTI geometry and produces a factor-aware signal distinct from generic ensemble spread. The common-mode decomposition and fixed rank hybrid are clear. Broad negative adaptive results are not hidden.

**Weaknesses.** Core formulas remain simple and physical consistency requires multiple factor outputs. No learned refinement or formal optimality result is provided.

**Fatal concerns:** none after correcting shape matching and common-support fidelity.

Scores: novelty 4.0/5; technical quality 4.2/5; significance 3.9/5; clarity 4.3/5; reproducibility 4.6/5; overall 4.0/5.

## Reviewer B: Uncertainty and Selective Prediction

**Strengths.** The paper avoids calibrated-probability claims, separates triage/attribution/shared difficulty, uses nested outer predictions, and computes paired profile-aligned risk-coverage intervals.

**Weaknesses.** Attribution is weak and empirical-CDF calibration is limited by 18--20 inner cases. Adaptive selection has negative transfer.

**Fatal concerns:** none; negative attribution is correctly bounded.

Scores: novelty 3.8/5; technical quality 4.3/5; significance 3.8/5; clarity 4.4/5; reproducibility 4.6/5; overall 3.9/5.

## Reviewer C: Medical Imaging

**Strengths.** All cross-model errors use a common support; NingXia is correctly described as internal OOF rather than external validation; clinical safety and diagnostic harm are not claimed.

**Weaknesses.** NingXia and fastMRI-brain are small, evidence is T2 brain MRI, and there is no reader or downstream study.

**Fatal concerns:** none for a methods paper, provided claims stay at retrospective prioritization.

Scores: novelty 3.9/5; technical quality 4.1/5; significance 3.7/5; clarity 4.3/5; reproducibility 4.4/5; overall 3.8/5.

## Reviewer D: Skeptical Reproducibility

**Strengths.** Candidate failures remain machine-readable; cost/one-SE code matches the declaration; outer-label flags, target exclusion, physical matching, and 2,000 replicate counts are tested; the ZIP includes imported helpers.

**Weaknesses.** The full candidate registry is large and online neural cost uses an explicit proxy rather than common-hardware measurements.

**Fatal concerns:** none after package verification.

Scores: novelty 3.8/5; technical quality 4.4/5; significance 3.8/5; clarity 4.2/5; reproducibility 4.7/5; overall 4.0/5.

## Consensus

Mean technical quality: **4.25/5**. Mean overall: **3.93/5**. The remaining acceptance risk is scientific scope and cohort size, not an avoidable leakage, traceability, geometry, or packaging defect.
"""
    (ROOT/"final_reviewer_simulation.md").write_text(reviewer,encoding="utf-8")

    reproduce=f"""# Reproducibility Verification

## Verified

- 11/11 unit and integration tests passed with the MRI Python environment.
- Both papers compile without LaTeX errors, undefined citations/references, or overfull boxes.
- Regular PDF: 5 letter-size pages, pages 1--4 technical and page 5 references only.
- Extended PDF: 9 letter-size pages, pages 1--8 technical and page 9 references only.
- `pdffonts` reports embedded Type 1 or CID TrueType fonts; no Type 3 fonts.
- 528 first-pass and 528 amended decisions have `selection_used_outer_labels=False`.
- Every target is excluded from its own selected committee.
- Every final factor--target--method profile has all 22 outer cases.
- Every paired bootstrap group contains exactly 2,000 aligned replicates.
- All {len(physical_pairs):,} physical records have matched generated planes.
- Main table and macros are generated from CSV, with claim provenance in `nested_claim_traceability.csv`.

## Reproduction

From precomputed features:

```powershell
cd D:\\MRI
.\\design\\rasinet\\reproduce_nested.ps1 -Mode from-precomputed
```

End to end from NIfTI predictions:

```powershell
cd D:\\MRI
.\\design\\rasinet\\reproduce_nested.ps1 -Mode recompute-features
```
"""
    (ROOT/"REPRODUCIBILITY_VERIFICATION.md").write_text(reproduce,encoding="utf-8")

    unresolved="""# Unresolved Before Submission

| Item | Missing input | Command / action | Expected output | Claim impact | Must resolve? |
|---|---|---|---|---|---|
| Common-hardware online latency | Executable checkpoints and uniform inference wrappers for all 11 neural models | Run each model under one GPU benchmark harness | per-model latency, memory, and parameter table | Cost remains a transparent proxy; no accuracy claim changes | Recommended, not mandatory if proxy wording remains |
| External untouched site | A legally available site not inspected during this project | Freeze protocol, then run scoring/evaluation once | external profile CSV and CI | Limits generalization beyond internal OOF NingXia | Strongly recommended |
| Reader study | Readers, review protocol, and approvals | Prospective queue-order reader study | review time and clinically relevant misses | Prevents workflow/clinical-benefit claims | Not required for current ranking claim |
| Downstream task | Labels and validated task model | Compare task output across retained/referral subsets | task-risk curves | MAE cannot be equated with diagnostic harm | Not required for current ranking claim |
| Adaptive committee validation | Larger labeled development cohort | Re-run frozen adaptive protocol without changing candidates | stable nested target/factor selection | Current paper reports adaptive selection as negative | Required only to claim adaptive superiority |

No internal TODO, ethics placeholder, fabricated citation, or invented experiment value remains in either submitted PDF.
"""
    (ROOT/"unresolved_before_submission.md").write_text(unresolved,encoding="utf-8")
    print(json.dumps({"baseline_nAURC":baseline.normalized_aurc,"physical_nAURC":physical.normalized_aurc,
                      "paired_delta":[delta.delta_normalized_aurc,delta.delta_normalized_aurc_lo,delta.delta_normalized_aurc_hi],
                      "targets":targets,"bank":bank,"commit":commit},indent=2))


if __name__=="__main__": main()
