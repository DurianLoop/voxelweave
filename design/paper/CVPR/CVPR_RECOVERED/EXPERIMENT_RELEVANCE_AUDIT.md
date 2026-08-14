# Experiment Relevance Audit, Plans 1–7

Central claim used for classification:

> In the evaluated deterministic MRI slice-interpolation settings, shared local estimator influence is one determinant of error alignment and therefore of disagreement blindness; target-preserving measurement-disjoint contexts expose error better than dependence-preserving controls. Anchor-CV is a lightweight examination-level consequence, not a universally superior score.

Classification is based on relevance to this claim, never on whether an outcome is favorable.

## Plans 1–2: discovery and validity controls

| Experiment / artifact | Result | Class | Manuscript disposition |
|---|---|---|---|
| Frozen Physical Consistency baseline and committee comparison | Established reproducible disagreement ranking and corrected committee accounting | SUPPORTING | Condense to motivation/baseline description; details remain in historical logs |
| Case influence, clustered validity, leave-one-case/patient analyses | fastMRI robust; NingXia uncertainty wider with eight patient clusters | SUPPORTING | Patient hierarchy stated in Methods and supplement |
| Heterogeneity and risk–coverage | Effect varies by cohort/profile but survives key strata | SUPPORTING | Selected risk evidence in supplement |
| Common-mode mechanism E010 | General detection hypothesis falsified; consistent-wrong cases exist | CORE / BOUNDARY | Keep consensus-blindness phenomenon and one-sided boundary |
| Context controls and geometry audit | 1,518/1,518 geometry checks valid; no plane mismatch | SUPPORTING | Short Methods statement; full audit referenced |
| Intensity confounding / normalization | Raw scale contributes to ranking; independent output normalization invalid | BOUNDARY | Supplement; prevents scale-invariant claims |
| TTA comparator | Physical context generally stronger, but uniqueness versus all perturbations unresolved | SUPPORTING / BOUNDARY | Compact supplementary robustness result |
| Localization studies | Examination score does not reliably localize worst plane | BOUNDARY | Explicit supplement limitation |
| Endpoint sensitivity / factor-pair analyses | No single monotone-distance or factor-pair explanation | EXPLORATORY-NONCENTRAL | Exclude from main; retain internal record |

## Plan 3: shared difficulty and error structure

| Experiment | Result | Class | Manuscript disposition |
|---|---|---|---|
| Bias/diversity and shared-difficulty decomposition | Shared consensus error dominates observable diversity (80.9%/86.5% in original contexts) | CORE | Introduce phenomenon; clean-control decomposition supplies main quantitative version |
| Variance decomposition across case/model/scale | Case effects dominate architecture effects | SUPPORTING | One concise result supporting architecture-stable difficulty |
| Full model-family bank and IXI replication | Median pairwise error rho .961 (11 fastMRI neural families) and .991 (six IXI methods) | SUPPORTING | Supplement/generalization statement |
| Scale/factor ordering x2<x4<x6 | 138/138 case–architecture units obey ordering | SUPPORTING | Supplement; not needed for central mechanism |
| Shared-anchor boundary/curvature/deletion | Local boundary stable-wrong mechanism supported | SUPPORTING | Supplement failure analysis |
| TTA joint comparison | Physical sampling context beats flip-TTA in 18/18 profiles | SUPPORTING | Supplement |
| Pre-reconstruction/IXI acquired difficulty | Adjacent-slice RMSE strongly tracks raw error, especially IXI | BOUNDARY / SUPPORTING | Required as strong trivial baseline for Anchor-CV |
| Spectral-spatial, motion, triangle, diversity-only hypotheses | High-frequency, motion and diversity-only accounts rejected | EXPLORATORY-NONCENTRAL | Exclude from main; retain logs |
| Naive PC/input fusion | Degrades ranking | EXPLORATORY-NONCENTRAL | Supplement negative-result ledger only |

## Plans 4–5: controlled intervention and mechanism refinement

| ID | Result | Class | Manuscript disposition |
|---|---|---|---|
| Plan4 disjoint anchor intervention (HAT/SwinIR) | Strong error ranking on fastMRI/NingXia | CORE | Main controlled-intervention section |
| Plan4 analytical disjoint (linear/cubic) | Same direction across analytical estimators/cohorts | SUPPORTING | Main compact cross-estimator sentence/table; full detail supplement |
| Plan4 maximum-shared and zero-vs-max paired control | Sharing lowers observability and ranking under same target | CORE | Main figure/table |
| Plan4 NingXia disjoint replication | Direction supported with patient clustering | SUPPORTING / BOUNDARY | Keep as small-cohort replication, not co-equal power |
| Overlap paired levels | Mixed precision at intermediate levels | BOUNDARY | Supplement; motivates exact ladder |
| Adaptive acquisition and baselines | Retrospective benefit prediction; no universal winner | SUPPORTING / BOUNDARY | Replaced by frozen Plan6 consequence in main |
| C5-E001 manifest freeze | 759 eligible rows, 161 case/series files, 147 patient clusters | SUPPORTING | Reproducibility statement |
| C5-E002 covariance chain | Full chain on IXI/NingXia; reversal control confounded on fastMRI | CORE / BOUNDARY | Use clean control in main; confounded reversal in supplement |
| C5-E003 clean maximal-sharing control | Disjoint-minus-shared rho positive with intervals above zero in all cohorts | CORE | Main Figure 2 and core table |
| C5-E004 budget curves | Near oracle on fastMRI, not universally best on NingXia | SUPPORTING / BOUNDARY | Supplement only; superseded by frozen Plan6 pair |
| C5-E005 IXI replication | 115-case clean-control confirmation | CORE | Main primary cohort evidence |
| C5-E006 orthogonal two-component model | Frozen confirmation gate failed | EXPLORATORY-NONCENTRAL | Exclude main; evidence-selection audit records it |
| C5-E007–E009 acquired-anchor bipartition and budgets | Positive error/benefit ranking, not universal | SUPPORTING | Supplement; Anchor-CV is simpler consequence |
| C5-E010 stable-wrong prevalence | Clean sharing raises high-error/low-disagreement prevalence in all cohorts | SUPPORTING | Main concise sentence, detailed supplement |
| C5-E011 Anchor-CV | Strong examination-level ranking; failed localization; initially appeared better than RMSE under narrower baselines | SUPPORTING / BOUNDARY | Main practical consequence with later Plan6 strong-baseline correction |
| C5-E012/C5-E013 exact overlap ladders | Strong overall trends but preserved 0→1 reversal | CORE | Main falsification of count-only law |
| C5-E014 analytical shared influence | Influence exceeds count for alignment/observability in all cohorts | CORE | Main mechanism refinement |

## Plan 6: confirmation and practical consequence

| ID | Result | Class | Manuscript disposition |
|---|---|---|---|
| P6-E01 metric robustness | 42/42 disjoint-minus-shared endpoint directions positive; SSIM/gradient boundaries | SUPPORTING / BOUNDARY | Supplement; prevents metric-independent claim |
| P6-E02 consensus distributions | Shared fraction strongly suppresses normalized disagreement; strict plane stable-wrong rare | CORE / BOUNDARY | Main decomposition; prevalence nuance supplement |
| P6-E03 geometry/normalization | Geometry valid; shared scaling preserves effect; rank changes under normalization | SUPPORTING / BOUNDARY | Supplement |
| P6-E04 neural shared influence | 18/18 primary advantages over count; fixed-count succeeds fastMRI/IXI, fails NingXia | CORE / BOUNDARY | Main Figure 3 and central results |
| P6-E05 mechanism chain | All local arrows supported; global context-ranking arrow only 3/6 | CORE / BOUNDARY | Main with explicit non-mediation language |
| P6-E06 Anchor-CV audit | rho .943/.955/.958, but no consistent information beyond adjacent MAE/scale/spacing | SUPPORTING / BOUNDARY | Main Figure 4; no superiority claim |
| P6-E07 frozen risk and x4→x2 consequence | Strong triage and benefit ranking; no universal winner; IXI cross-estimator | SUPPORTING / BOUNDARY | Main practical consequence and supplement curves |
| P6-E08 architecture-independent difficulty | Examination identity dominates; naive feature stacking fails | SUPPORTING | Main one sentence; stacking failure supplement |
| P6-E09 failure taxonomy | Scores usually concordant and do not localize worst plane | BOUNDARY | Supplement |
| P6-E10 efficiency | Anchor-CV requires zero neural calls and milliseconds; ranking not superior | SUPPORTING | Discussion/supplement |
| P6-E11 analytical factor robustness | Shared error rises and observability falls x2→x4→x6 | SUPPORTING | Supplement |
| P6-E12 full risk–coverage | Disjoint beats dependence-preserving output scores; adjacent MAE wins NingXia | SUPPORTING / BOUNDARY | Supplement and discussion |

## Plan 7: adversarial capability and stability tests

| ID | Result | Class | Manuscript disposition |
|---|---|---|---|
| P7-CV-E01 minimum-influence context selection | Strong local fastMRI result but below random/PC on IXI; heterogeneous NingXia | EXPLORATORY-NONCENTRAL | Exclude main; disclose in supplement negative ledger because it limits prescriptive use |
| P7-CV-E02 perturbation/plane stability | All 42 perturbation strata pass; two of three plane gates fail | SUPPORTING / BOUNDARY | Main local-property wording; full table supplement |
| P7-CV-E03 multi-anchor jackknife IQR | Confirmation and transfer gates fail badly | EXPLORATORY-NONCENTRAL | Exclude main; evidence-selection audit only, optional supplement ledger |
| P7-CV-E04 covariance residualization | Negligible/mixed transfer gain; locked gate fails | EXPLORATORY-NONCENTRAL | Exclude main; evidence-selection audit only, optional supplement ledger |
| P7 TMI operational/metric/regime experiments | Address the related journal framing, not the CVPR influence claim | REDUNDANT for CVPR | Exclude from CVPR; remain in Plan7/TMI records |

## Audit conclusion

No excluded experiment materially contradicts the final central mechanism claim. The required contradictory/bounding evidence—nonmonotone count ladder, NingXia fixed-count null/mixed result, weak context-ranking arrow, plane dependence, Anchor-CV non-superiority/localization failure, and retrospective-only acquisition consequence—must remain visible in the main paper or supplement.
