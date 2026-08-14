# Verified Literature Map

Verification date: 2026-08-12. Entries below were checked from the paper/official record, not inferred from titles.

## MRI reconstruction uncertainty and error prediction

### Hu, Pezzotti, and Welling — Learning to Predict Error for MRI Reconstruction

- Venue/year: MICCAI 2021.
- URL/DOI: https://doi.org/10.1007/978-3-030-87199-4_57
- Core idea: decomposes prediction error into systematic and random components and trains a separate model to predict error magnitude.
- Relevance: strongest direct precedent for ground-truth-free error estimation.
- Difference: requires supervised error-predictor training; current work uses only stored deterministic outputs and ranks cases.
- Novelty threat: high to any generic "predict reconstruction error" claim; not fatal to physical cross-factor consistency.

### Edupuganti et al. — Uncertainty Quantification in Deep MRI Reconstruction

- Venue/year: IEEE Transactions on Medical Imaging, 2021.
- DOI: https://doi.org/10.1109/TMI.2020.3025065
- Core idea: probabilistic VAE reconstruction, Monte Carlo variance, and SURE-based risk estimation.
- Difference: posterior/acquisition uncertainty in undersampled MRI, not deterministic through-plane interpolation across physical planes.
- Novelty threat: high to calibrated-UQ language; supports avoiding that language.

### Küstner et al. — Predictive Uncertainty in Deep Learning-Based MR Image Reconstruction Using Deep Ensembles

- Venue/year: Magnetic Resonance in Medicine, 2024.
- DOI: https://doi.org/10.1002/mrm.30030
- Core idea: evaluates pixelwise predictive uncertainty from deep ensembles on fastMRI.
- Difference: repeated trained models of a reconstruction method versus heterogeneous fixed outputs and same-target cross-factor behavior.
- Novelty threat: moderate to cross-model disagreement, low to physical consistency.

### Zhang, Bi, and Fung — On the Quantification of Image Reconstruction Uncertainty Without Training Data

- Venue/year: WACV 2024.
- URL: https://openaccess.thecvf.com/content/WACV2024/html/Zhang_On_the_Quantification_of_Image_Reconstruction_Uncertainty_Without_Training_Data_WACV_2024_paper.html
- Core idea: training-data-free image reconstruction uncertainty.
- Difference: general inverse-problem uncertainty formulation, not MRI slice-review ranking from factor-aligned stored outputs.
- Novelty threat: moderate; requires careful distinction from "training-free UQ."

### Giannakopoulos et al. — Pixelwise Uncertainty Quantification of Accelerated MRI Reconstruction

- Venue/year: arXiv preprint, 2026; not peer reviewed as of verification.
- URL: https://pubmed.ncbi.nlm.nih.gov/41647209/
- Core idea: conformal quantile regression learns pixelwise intervals for accelerated brain/knee MRI over factors 2–10.
- Difference: trained quantile models and interval coverage versus training-free retrospective case ranking.
- Novelty threat: high to future pixelwise/coverage claims, not equivalent to current mechanism.

## MRI quality assessment

### Shaw et al. — A Heteroscedastic Uncertainty Model for Decoupling Sources of MRI Image Quality

- Venue/year: MIDL 2020, PMLR 121.
- URL: https://proceedings.mlr.press/v121/shaw20a.html
- Core idea: heteroscedastic reconstruction model distinguishes recoverable corruption and downstream suitability.
- Difference: trained quality model for corrupted MRI; current endpoint is error-based selective review of interpolation outputs.
- Novelty threat: moderate and reinforces that visual quality is not diagnostic/task quality.

### Stepien et al. — A Brief Survey on No-Reference Image Quality Assessment Methods for Magnetic Resonance Images

- Venue/year: Journal of Imaging, 2022.
- DOI: https://doi.org/10.3390/jimaging8060160
- Core idea: surveys no-reference MRI IQA, mainly perceptual/acquisition quality.
- Difference: current score targets reconstruction-error ordering for a specified interpolator.
- Novelty threat: low if the endpoint remains explicit.

## Selective prediction and evaluation

### Ding et al. — Revisiting the Evaluation of Uncertainty Estimation and Its Application to Explore Model Complexity–Uncertainty Trade-Off

- Venue/year: CVPR Workshops 2020.
- URL: https://openaccess.thecvf.com/content_CVPRW_2020/html/w50/Ding_Revisiting_the_Evaluation_of_Uncertainty_Estimation_and_Its_Application_to_Explore_CVPRW_2020_paper.html
- Core idea: motivates risk-coverage/AURC evaluation for confidence ranking.
- Difference: generic predictive evaluation; provides the metric framework rather than the MRI signal.
- Novelty threat: none to method, essential to evaluation.

### Zhou et al. — A Novel Characterization of the Population AURC and Rates of Finite Sample Estimators

- Venue/year: ICML 2025.
- URL: https://proceedings.mlr.press/v267/zhou25y.html
- Core idea: formal population AURC and consistent finite-sample plug-in estimators.
- Relevance: warns that finite-sample AURC needs principled statistical treatment.
- Difference: theory/evaluation, not MRI reliability scoring.
- Novelty threat: none; motivates cautious small-cohort intervals.

## Reconstruction task baseline

### Song et al. — I3Net: Inter-Intra-slice Interpolation Network for Medical Slice Synthesis

- Venue/year: IEEE Transactions on Medical Imaging, 2024.
- DOI: https://doi.org/10.1109/TMI.2024.3394033
- Core idea: inter-/intra-slice modeling for medical slice interpolation.
- Relevance: strongest recurring reconstruction target/baseline in the local corpus.
- Difference: improves reconstructed images; current work assesses reliability after reconstruction.
- Novelty threat: none to ranking, but any reconstruction-quality claim must compare fairly with it.

## Novelty conclusion

No verified work above is materially equivalent to using same-target, world-coordinate-matched cross-interpolation-factor disagreement as a case-level selective-review score. This is a bounded literature conclusion, not a universal priority claim.

## Plan-2 surveillance additions (verified 2026-08-12)

### Trautmann et al. — How Should We Evaluate Uncertainty in Accelerated MRI Reconstruction?

- Year/status: 2025 arXiv preprint.
- URL: https://arxiv.org/abs/2503.10527
- Core idea: evaluates ensemble reconstruction variability through registration and segmentation, showing that pixel metrics can coexist with anatomical bias.
- Difference: downstream evaluation of probabilistic/ensemble variation rather than training-free physical-plane context disagreement.
- Novelty threat: high to any implication that pixelwise MAE association proves downstream relevance.

### Fischer et al. — CUTE-MRI: Conformalized Uncertainty-based Framework for Time-adaptivE MRI

- Year/status: 2025 arXiv preprint.
- URL: https://arxiv.org/abs/2508.14952
- Core idea: propagates probabilistic reconstruction uncertainty to task metrics and conformalizes the interval for adaptive acquisition stopping.
- Difference: probabilistic, task-level, calibrated acquisition control versus retrospective deterministic output ranking.
- Novelty threat: high to calibration/clinical-control claims; not equivalent to PC-v1.

### Alçalar and Akçakaya — Sparsity-Driven Parallel Imaging Consistency for Improved Self-Supervised MRI Reconstruction

- Venue/year: ICIP 2025.
- DOI: https://doi.org/10.1109/ICIP55913.2025.11084355
- Core idea: trains MRI reconstruction with perturbations and a sparse-domain consistency objective.
- Difference: consistency is a training loss in k-space reconstruction; PC is a post-hoc reliability witness for through-plane interpolation on matched world planes.
- Novelty threat: establishes that perturbation consistency itself is prior art; the contribution cannot be framed generically.

### Arvinte et al. — MRI Acquisition and Reconstruction Cookbook: Recipes for Reproducibility, Served with Real-World Flavour

- Venue/year: Magnetic Resonance Materials in Physics, Biology and Medicine, 2025.
- URL: https://link.springer.com/article/10.1007/s10334-025-01236-4
- Core idea: documents reconstruction reproducibility and sensitivity of reference metrics to masks, noise, and reference choices.
- Relevance: directly motivates the endpoint/mask/intensity confounder audit.
- Novelty threat: none to PC; important methodological constraint.

### Giannakopoulos et al. — Pixelwise Uncertainty Quantification of Accelerated MRI Reconstruction

- Updated status: January 2026 arXiv preprint, not peer reviewed at verification.
- URL: https://pubmed.ncbi.nlm.nih.gov/41647209/
- Core idea: conformal quantile-regression intervals for brain and knee fastMRI across acceleration 2–10.
- Difference: learned/calibrated intervals versus deterministic context discrepancy.
- Novelty threat: substantial to broad pixelwise-UQ claims; PC must remain an uncalibrated association/witness.

## Plan-3 broader inverse-problem surveillance (verified 2026-08-13)

### Wood et al. — A Unified Theory of Diversity in Ensemble Learning

- Venue/year: JMLR 2023.
- URL: https://www.jmlr.org/papers/v24/23-0041.html
- Core result: diversity is a model-fit term inside exact bias–variance–diversity decompositions; maximizing diversity alone is not generally justified.
- Relevance: directly anticipates E019's negative result and supports the refined intervention principle: diversity must be balanced with target preservation and individual/shared error.
- Difference: supervised ensemble prediction rather than target-preserving reconstruction contexts.

### Ohayon, Michaeli, and Elad — The Perception–Robustness Tradeoff in Deterministic Image Restoration

- Venue/year: ICML 2024.
- URL: https://proceedings.mlr.press/v235/ohayon24a.html
- Core result: deterministic inverse-problem estimators face a formal trade-off between perceptual quality, measurement consistency, and robustness/Lipschitz behavior.
- Relevance: connects context sensitivity to a broader deterministic restoration phenomenon and cautions that stability cannot be interpreted independently of reconstruction objectives.
- Difference: adversarial/measurement robustness theory, not post-hoc error witnessing.

### Xia and Chakrabarti — Training Image Estimators without Image Ground-Truth

- Year: 2019 preprint.
- URL: https://arxiv.org/abs/1906.05775
- Core result: paired varied measurements plus known forward models can train estimators without clean targets when measurement diversity is sufficient.
- Relevance: close conceptual precedent for exploiting multiple target-preserving measurements; it concerns training, whereas this project concerns post-hoc reliability.

### Zheng, Dewil, and Arias — Self-Supervised Uncertainty Estimation for Super-Resolution of Satellite Images

- Year/status: 2026 preprint.
- URL: https://arxiv.org/abs/2603.14074
- Core result: redundant low-resolution observations support self-supervised posterior mean/variance learning and calibrated intervals in synthetic satellite SR.
- Relevance: strong collision with any broad claim that multi-observation, ground-truth-free restoration uncertainty is new.
- Difference: learned probabilistic/calibrated uncertainty versus deterministic, untrained, one-sided witnesses.

### Savant — Deep Learning for MRI Slice Interpolation: The Critical Role of Problem Formulation

- Year/status: 2026 preprint.
- URL: https://arxiv.org/abs/2605.16476
- Core observation: changing adjacent-slice context had a much larger effect than architecture changes in prostate slice interpolation.
- Relevance: independently aligns with E016/E023 that context/problem formulation can dominate architecture, although task, anatomy, and evaluation differ.
- Novelty threat: high to a generic “architecture matters less than context” claim; our contribution must be the quantitative latent-difficulty/shared-error decomposition and reliability implications.
