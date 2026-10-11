# Two-source fixed-denominator sensitivity: result

**Status:** Post-result algebraic sensitivity analysis of the original IXI-trained HAT/SwinIR pair. The [rule](FIXED_DENOMINATOR_TWO_SOURCE_PLAN_2026-10-01.md) was written before this calculation, after the main positive results were known. No images or model checkpoints were decoded and no GPU inference was run. It is not another cohort or independent experiment.

## Estimand and complete-cohort result

For each original target, keep the shared-condition paired MSE `T_s` as the denominator in both conditions. Let `D_s` and `D_d` be output disagreement MSE on the original fixed acquired-only mask. Define `Q_s=D_s/(4T_s)=O_s`, `Q_d=D_d/(4T_s)=O_d*T_d/T_s`, and `Delta Q=Q_d-Q_s`. ReMIND's stored `D` values were checked directly against `4TO`; MSValid's `D` was reconstructed from its original `O` and `T`. Targets, patients, support and model outputs are unchanged. `T_s` still requires the withheld target, so `Q` is retrospective and cannot be used as a deployment score.

Targets were first averaged within residue 1/3, residues equally within patient, then patients equally. ReMIND's interval resamples ordinary T2 and BLADE separately with the original completed group weights. Both 5,000-draw percentile intervals use the original source-specific bootstrap seeds, but are **exploratory post-result intervals**.

| Source | Patients / targets | Shared `Q` | Disjoint `Q` | `Delta Q`, percentage points | 95% patient interval, points | Positive patients / targets | Original `Delta O`, points |
|---|---:|---:|---:|---:|---:|---:|---:|
| MSValid RRMS T2 | 84 / 479 | 1.042010% | 25.257248% | **+24.215238** | +23.688606 to +24.732011 | 84/84; 479/479 | +24.185623 |
| ReMIND preoperative T2 | 62 / 248 | 1.109256% | 27.601081% | **+26.491825** | +25.738174 to +27.291657 | 62/62; 248/248 | +26.399912 |

ReMIND's ordinary T2 and BLADE groups had mean `Delta Q` of +26.849802 and +26.027782 points, with 35/35 and 27/27 patients positive. The fixed-denominator contrast exceeds the original `Delta O` by +0.029615 points in MSValid and +0.091913 points in ReMIND. These differences are descriptive algebraic consequences of changing the denominator, **not** estimates of a causal denominator contribution. The important check is that the large positive contrast remains when each target uses the same denominator in both conditions. Indeed, the stored/reconstructed raw `D_d-D_s` is positive for every original target in both sources.

This rules out a changing paired-MSE denominator as the sole explanation of the observed contrast. It does not isolate original acquisition identity: changing phase still changes the companion's complete neighboring images, signed geometry, possibly normalization and ReMIND publication processing. The [native-linear control](PUBLIC_LINEAR_PARTNER_CONTROL_RESULT_2026-10-01.md) separately shows the phase effect is not specific to two learned models. These two observations narrow the paper to a published-context audit, not a novel network mechanism.

## Integrity and reproduction

The analysis required unchanged SHA-256 values of both original per-target, per-patient and summary files; reproduced the original patient-weighted `Delta O` exactly; and refused to overwrite original or existing output. The [independent read-only verifier](experiments/verify_fixed_denominator_two_source.py) separately recalculated target `Q` with decimal arithmetic, patient/residue means, signs and both bootstrap intervals and passed both sources. Result files are [summary](experiments/fixed_denominator_two_source/summary.json), [per-patient CSV](experiments/fixed_denominator_two_source/per_patient.csv) and [per-target CSV](experiments/fixed_denominator_two_source/per_target.csv). The [analysis script](experiments/fixed_denominator_two_source.py) and its input hashes are recorded in the summary. The CSVs preserve source patient labels and remain internal until release review.

Run from `D:\MRI`: `D:\conda\envs\MRI\python.exe -B innovation\experiments\verify_fixed_denominator_two_source.py`.
