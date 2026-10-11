# Novelty collision audit

Audit date: 2026-08-13. Search concepts: leave-one-slice-out MRI, interpolation cross-validation, reconstruction error prediction, dependent ensemble uncertainty, common-mode error, measurement influence, active acquisition and densification value. “No” means the paper record does not use the same construct as this work; it is not a claim that the broader idea is absent from all literature.

## Ten closest works

| Prior work | Same target? | Same physical measurement intervention? | Explicit shared influence / dependent error? | Acquired-only CV? | Same endpoint? | Main collision and retained difference |
|---|---|---|---|---|---|---|
| Hu et al., [Learning to Predict Error for MRI Reconstruction](https://miccai2021.org/openaccess/paperlinks/2021/09/01/280-Paper1009.html), MICCAI 2021 | MRI reconstruction error | No | Systematic-error blindness, yes conceptually | No | Error prediction | **Closest conceptual collision:** already shows variability can miss systematic error. Retained difference is the same-target physical anchor-reuse intervention and measured error-alignment chain. |
| Horváth et al., [High Order Slice Interpolation for Medical Images](https://doi.org/10.1007/978-3-319-68127-6_8), SASHIMI 2017 | Slice interpolation | No | No | Yes, leave-one-slice-out evaluation | Interpolation error | **Closest operation collision:** withholding a slice is not new. Retained difference is using acquired anchors as a deployment score and auditing dependence, not proposing holdout validation. |
| Edupuganti et al., [Uncertainty Quantification in Deep MRI Reconstruction](https://pubmed.ncbi.nlm.nih.gov/32956045/), TMI 2021 | MRI reconstruction | No | Bias plus variance recognized | No | Risk/MSE and uncertainty | Collides with MRI reliability motivation; differs in posterior/SURE method and k-space reconstruction setting. |
| Narnhofer et al., [Bayesian Uncertainty Estimation](https://pubmed.ncbi.nlm.nih.gov/34506279/), TMI 2022 | MRI reconstruction | No | Epistemic uncertainty, not physical reuse | No | Pixel uncertainty | Collides with uncertainty scope; does not manipulate shared acquired evidence between paired deterministic estimates. |
| Tezcan et al., [Sampling Possible Reconstructions](https://pubmed.ncbi.nlm.nih.gov/35143393/), TMI 2022 | MRI reconstruction | No | Posterior sample dependence not central | No | Reconstruction uncertainty | Collides with multiple plausible reconstructions; differs from deterministic agreement blindness and measurement-overlap controls. |
| Küstner et al., [Predictive Uncertainty Using Deep Ensembles](https://doi.org/10.1002/mrm.30030), MRM 2024 | MRI reconstruction | No | Dependent trained estimators are relevant | No | Ensemble uncertainty/error | Closest ensemble comparator; architecture committee is audited here but physical measurement reuse is the controlled variable. |
| van der Velde et al., [Aleatoric uncertainty in accelerated prostate MRI](https://pubmed.ncbi.nlm.nih.gov/42192056/), 2026 | MRI reconstruction | Perturbs/omits echo trains, but no paired same-target overlap ladder | Acquisition perturbation dependence is discussed through coil sensitivity | No | Variance-error correlation | Important near-collision: inference perturbations expose acquisition fragility, yet do not isolate reused physical anchors or shared paired-error energy. Cite and narrow claims. |
| Zhang et al., [Reducing Uncertainty With Active Acquisition](https://openaccess.thecvf.com/content_CVPR_2019/html/Zhang_Reducing_Uncertainty_in_Undersampled_MRI_Reconstruction_With_Active_Acquisition_CVPR_2019_paper.html), CVPR 2019 | MRI reconstruction | Changes k-space acquisition | Uses learned uncertainty, not paired shared influence | No | Reconstruction improvement | Collides with “additional measurements have value.” Our evidence is retrospective value prediction only, never prospective optimization. |
| Cole et al., [Active Acquisition for Multimodal Neuroimaging](https://pmc.ncbi.nlm.nih.gov/articles/PMC6807153/), 2019 | Neuroimaging completion | Selects additional modalities | No shared-error mechanism | No | Acquisition utility | Prevents broad “first value-of-acquisition prediction” wording; through-plane measurement dependence and frozen budgets remain different. |
| Zhang et al., [Quantification of Image Reconstruction Uncertainty Without Training Data](https://openaccess.thecvf.com/content/WACV2024/html/Zhang_On_the_Quantification_of_Image_Reconstruction_Uncertainty_Without_Training_Data_WACV_2024_paper.html), WACV 2024 | General/MRI reconstruction | No paired anchor-reuse intervention | Models data uncertainty | No | Reconstruction uncertainty | Collides with target-free uncertainty goal; differs in posterior variational estimation and the dependency failure being studied. |

## Collision verdict by claim

| Candidate claim | Verdict | Required wording/action |
|---|---|---|
| “Disagreement can miss common error.” | SUBSUMED / textbook-level | Never claim as novel; use only as motivation. |
| “Uncertainty can miss systematic MRI reconstruction error.” | SUBSUMED by Hu et al. | Cite directly and state that physical source/control is the new question. |
| “Leave-one-slice-out interpolation QA.” | OPERATION PRECEDED by Horváth et al. | Anchor-CV cannot be presented as a new operation. |
| “Additional MRI measurements can be selected by expected benefit.” | BROADLY PRECEDED by active acquisition | Retain only retrospective densification-value prediction; no prospective-policy wording. |
| “Physical anchor reuse changes paired deterministic error alignment and error observability for the same interpolated plane.” | NO DIRECT COLLISION FOUND IN THIS SEARCH | Defensible TMI distinction; avoid “first.” |
| “Finite-difference shared neural anchor influence explains error geometry beyond integer overlap.” | NO DIRECT COLLISION FOUND, BUT INFLUENCE/attribution literature is broad | Defensible CVPR mechanism if robustness passes; describe as a local response statistic, not a global attribution theorem. |
| “Influence-aware context selection/correction is superior.” | FALSIFIED BY PLAN7, irrespective of novelty | Remove from main contributions; retain negative results. |

## Search boundary and action

The audit found close conceptual and operational ancestors but no direct same-target physical-anchor reuse experiment with the full chain `reuse → aligned error → cancellation → lower observability`. This is a bounded search result, not proof of priority. Both bibliographies must cite Hu, Horváth, MRI posterior/ensemble uncertainty, active acquisition, and the 2026 acquisition-perturbation study before submission. Any later human literature check that finds a closer intervention overrides this matrix and requires narrower claims.

