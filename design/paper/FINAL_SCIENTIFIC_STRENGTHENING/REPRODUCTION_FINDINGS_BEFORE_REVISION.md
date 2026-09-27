# Findings recorded before manuscript revision

## R1: the original IXI Table 1 error endpoint is not fixed phase-0 error

Independent source inspection of `CVPR/archive/CVPR_UPGRADE/scripts/clean_max_overlap_flip.py` shows two different branches. For fastMRI/NingXia the fixed endpoint is `phase0_error` from the Plan 4 disjoint arrays. For IXI it is `mae` from `overlap_covariance_ixi_per_plane.csv`, which `overlap_covariance_chain.py::plane_metrics` defines as the average MAE of the two **disjoint** predictions. The shared and disjoint scores are therefore ranked against one common endpoint within each cohort, but the IXI endpoint is not the reference predictor's error alone.

The current main Table 1 caption and Figure 2 caption incorrectly call all three fixed phase-0 error. This is a semantic implementation/prose mismatch; it cannot be fixed by relabeling the point correlation as examination-level. The revised text must state pooled-plane correlation with a cohort-specific fixed endpoint: reference error for fastMRI/NingXia, disjoint-pair error for IXI. The new cross-architecture experiment separately and correctly uses fixed-reference error and condition-specific paired error as two distinct secondary estimands.

No historical number or source record is overwritten. Numerical reproduction will list any additional differences separately.

## R2: SAINT coordinate mapping

The existing SAINT wrapper divides local output z by output depth minus one. A shifted phase requires a physical origin, and using source depth only for phase2 can introduce a denominator mismatch with phase0. Before any new inference, execution amendment A1 fixes both new SAINT phases to physical z/(source depth-1). Legacy coordinates are retained in separate reproduction arrays. This is a declared interface correction, not a favorable-pair selection.

## Freeze bookkeeping

Initial asset freeze completed before A1 was made explicit. The original protocol bytes are preserved as `FINAL_ITERATION_PROTOCOL_V1.md` with the original SHA-256; `execution_freeze.json` binds the current amended protocol before the first model inference. An initial Windows text-write newline conversion failed the hash assertion; saving exact bytes resolved it before execution. Neither the original freeze nor any measured result was rewritten to conceal this issue.
