# Reviewer Attack Notes

## 1. Is this just ensemble disagreement?

Yes, the core signal belongs to the broader family of disagreement-based reliability measures. The contribution must not be framed as inventing ensemble variance. The defensible contribution is the target-specific formulation and evaluation protocol for through-plane MRI interpolation: deployment-compatible masking, separation of spatial localization from case triage, normalized risk--coverage evaluation, three-dataset validation, and explicit committee-composition sensitivity.

Evidence required:

- target excluded from committee by code and equation;
- target-to-committee score compared with shared dispersion;
- neural-only, analytical-only, and all-member committees;
- score-level leave-one-member-out analysis.

## 2. Why call this reliability rather than uncertainty?

The score is not a posterior variance, calibrated probability, or decomposition of aleatoric and epistemic uncertainty. Use `reliability score`, `disagreement score`, or `risk-ranking signal`. The paper may discuss uncertainty literature but must keep this semantic boundary explicit in the abstract, method, discussion, and conclusion.

## 3. Does background inflate pixel correlation?

Primary pixel correlation uses a foreground mask derived from the target prediction, not from ground truth. This preserves deployment feasibility. All-pixel correlation is secondary. Report foreground fraction and the difference between foreground and all-pixel results in supplementary data.

## 4. Does the method require multiple expensive models?

Yes. If outputs do not already exist, generating a committee can be expensive. The paper targets retrospective benchmarking, multi-model research pipelines, and environments where alternative reconstructions already exist. Do not claim universally negligible compute. Scoring cost is small relative to inference, but committee generation cost is outside the post-hoc metric runtime.

## 5. Why use linear and cubic interpolation?

They are analytical committee members and single-reference comparators, not the main reconstruction opponents. The analytical-only ablation tests whether simple references are sufficient. The neural-only ablation tests whether conclusions survive without them.

## 6. Is fastMRI AUROC of 1.000 credible?

It is a descriptive result from 24 cases and three failure positives. It must remain supplementary and always carry the sample count. Continuous risk--coverage metrics are primary because they use all cases and avoid a brittle binary threshold.

## 7. Are datasets comparable when MAE scales differ?

Raw MAE and raw AURC are not compared across datasets. Use normalized AURC relative to oracle and random rankings, plus relative risk reduction at fixed coverage. Dataset-specific MAE can still be reported at operating points.

## 8. Could all reconstructors fail together?

Yes. Consensus does not imply correctness. The qualitative false-reassurance case and leave-one-member-out analysis make this visible. The limitation is fundamental and should not be softened.

## 9. Why not train a learned uncertainty head?

A learned head addresses a different question and introduces training labels, architecture dependence, and calibration requirements. The current study asks how much quality-control signal is already present in heterogeneous stored outputs. TTA is retained as a single-model auxiliary alternative.

## 10. Does reconstruction error reflect clinical harm?

No. MAE correlation and review ranking establish technical quality control only. A diagnostic reader study, pathology-aware endpoints, and prospective workflow evaluation are outside the evidence available here and are stated as limitations.
