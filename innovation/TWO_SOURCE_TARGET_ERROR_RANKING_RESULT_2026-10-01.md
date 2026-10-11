# Does context disagreement rank higher-error target planes?

**Status:** Post-result retrospective information test, not an independent source confirmation or deployable detector. The [rule](TWO_SOURCE_TARGET_ERROR_RANKING_PLAN_2026-10-01.md) was fixed before the score-to-error associations were calculated. It reuses all original target rows from the IXI-trained HAT/SwinIR main pair and native-linear partner control; no images or weights were decoded and no GPU process was used.

## Contract and endpoint

The outcome is the fixed HAT phase-0 MAE against each withheld target on its original acquired-only support. Four scores are target-free **output-disagreement RMS** within the recorded inference: HAT/SwinIR shared or disjoint context, and HAT/native-linear shared or disjoint context. The scores were reconstructed as `sqrt(4*T*O)` from the original per-target CSVs. ReMIND's stored disagreement MSE was independently cross-checked; exact target/support/HAT-error joins were required for both sources. Crucially, phase-2 planes used by disjoint scores are not available when only the phase-0 x4 anchors are acquired. They are retrospective comparators, not practical scores for the sparse-input task.

Within each patient and residue, every pair of target planes was scored 1 for correctly ordering HAT MAE, 0 for the reverse order, and 0.5 for ties. Pair means were averaged across residues, then patients equally. This controls the most direct residue/relative-position comparison, but does not make this a new patient sample. MSValid contributed 84 patients, 479 targets and 651 within-residue pairs; ReMIND contributed 62 patients, 248 targets and 124 pairs (exactly two per residue per patient). No targets failed or were dropped.

| Patient-equal within-residue concordance | MSValid | ReMIND |
|---|---:|---:|
| HAT/SwinIR, shared | 0.6605 | 0.6129 |
| HAT/SwinIR, disjoint | **0.8017** | **0.6774** |
| HAT/native-linear, shared | 0.5985 | 0.4516 |
| HAT/native-linear, disjoint | 0.7066 | 0.5403 |

| Paired patient difference | MSValid mean [95% interval] | ReMIND mean [95% stratified interval] |
|---|---:|---:|
| SwinIR disjoint minus shared | +0.1411 [+0.0681, +0.2161] | +0.0645 [-0.0242, +0.1452] |
| Linear disjoint minus shared | +0.1081 [+0.0246, +0.1899] | +0.0887 [-0.0161, +0.1935] |
| Disjoint SwinIR minus disjoint linear | +0.0951 [+0.0516, +0.1447] | +0.1371 [+0.0645, +0.2097] |

The intervals are exploratory 5,000-draw paired patient bootstraps with source-specific frozen seeds; ReMIND resamples ordinary T2 and BLADE separately at 35/27 patients. The ReMIND ordinary and BLADE SwinIR disjoint-minus-shared point estimates were +0.0571 and +0.0741. The primary within-partner improvement is **not confirmed in ReMIND**: its interval includes zero, with 18 positive, 9 negative and 35 tied patient comparisons. Each patient contributes only two pair decisions, so concordance is coarse and ties in differences are common. MSValid has 45 positive, 16 negative and 23 tied patients for the same difference.

The disjoint SwinIR score exceeded the disjoint linear score in both sources under this fixed retrospective endpoint. That does not rescue a claim of a learned-network-specific *phase effect*: linear disjoint-minus-shared concordance is also positive in both point estimates, and the score levels differ between partners. Across-source confirmation of improved target ranking remains insufficient; multiple score comparisons and the earlier choice of model/source are not corrected by these bootstrap intervals. Neither a large mean `Delta O` nor this result establishes calibration, error thresholds, lesion safety or a deployable uncertainty measure. A future ranking claim needs an acquired-only score, an untouched patient source and comparison with supervised MRI error prediction under the same task.

## Reproduction and integrity

- [Pre-calculation rule](TWO_SOURCE_TARGET_ERROR_RANKING_PLAN_2026-10-01.md), SHA-256 `b6870b3830614075c2f9dca2e246e491b690414b5ff04b89f68ddd7df1f17b9b`.
- [Calculation script](experiments/two_source_target_error_ranking.py), SHA-256 `00f227b43d82ef88baa39175302504dd21076a6bd9c8114a13bbb0c301065a7e`; it checks all four input CSV hashes and refuses to overwrite output.
- [Independent verifier](experiments/verify_two_source_target_error_ranking.py) passed all exact target joins, score-square reconstructions, patient/residue concordances and paired/stratified bootstrap intervals.
- [Summary](experiments/two_source_target_error_ranking/summary.json), SHA-256 `37393633353f41e95f6222a2c2da497023c47e5cade8ab88545cfb7695eae0f4`; [per-patient CSV](experiments/two_source_target_error_ranking/per_patient.csv), SHA-256 `56aab9ac89437c1af129b713c1df03ab3b7270f1d39d583c10cd8b516b9be155`; [per-target CSV](experiments/two_source_target_error_ranking/per_target.csv), SHA-256 `fb0cc09d8ac430945e7e9b2b8372925ae8660f2815e5cb3aa16f583d6c8c8980`. CSVs contain original source patient labels and remain internal.

Run the verifier from `D:\MRI` with `D:\conda\envs\MRI\python.exe -B innovation\experiments\verify_two_source_target_error_ranking.py`.
