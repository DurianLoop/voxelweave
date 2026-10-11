# Plan6 Novelty Audit

Audit date: 2026-08-13. Scope: MRI inter-slice interpolation reliability, consensus blindness, measurement overlap, neural shared influence, and acquired-anchor cross-validation.

## 1. Search scope

Searches covered MRI slice interpolation uncertainty, leave-one-slice-out interpolation, MRI reconstruction error prediction, deep ensembles, conformal/pixelwise uncertainty, active acquisition, measurement influence, correlated ensemble errors, and dependent-error uncertainty. The audit prioritized primary papers and official venue pages.

## 2. Closest prior work

### MRI slice interpolation and synthesis

- Peng et al., **SAINT** (CVPR 2020) introduced spacing-aware medical slice synthesis and emphasized anisotropic resolution and variable upsampling factors. It advances interpolation quality, not reliability under dependent prediction contexts.
- Fang et al. (CVPR 2022) used cross-view mutual distillation for self-supervised medical slice synthesis. It treats agreement across views as complementary training knowledge, not as an audited deployment uncertainty signal.
- I3Net (TMI 2024) is a strong inter/intra-slice synthesis architecture. It motivates architecture coverage but does not analyze whether shared acquired slices align errors and suppress disagreement.
- Horvath et al. (SASHIMI 2017) evaluated high-order medical slice interpolation with **leave-one-slice-out** experiments. This is an important Anchor-CV precursor: leaving out acquired slices to evaluate interpolation quality is not new. Their use is algorithm evaluation against known held-out slices, not a frozen examination-level difficulty score for an already acquired sparse scan.
- Savant (arXiv 2026) reports that MRI slice-context formulation can dominate architecture choice. This reinforces the importance of context geometry but postdates the principal experiments and does not study reliability or measurement-overlap dependence.

### MRI reconstruction uncertainty and error prediction

- Hu, Pezzotti, and Welling, **Learning to Predict Error for MRI Reconstruction** (2020), explicitly decomposes prediction error into random and systematic components and argues that common uncertainty estimates correlate poorly with total error because they capture random variation. This is conceptually close to consensus blindness. Therefore, neither paper should claim the first observation that variance/disagreement misses systematic error.
- Küstner et al. (MRM 2024) train deep ensembles with aleatoric heads for pixelwise MRI reconstruction uncertainty and evaluate domain shifts. Their uncertainty requires model training/multiple members and concerns k-space reconstruction, not physical slice-context overlap.
- PixCUE (2023/2024) jointly predicts reconstruction and uncertainty in one forward pass. It is a learned uncertainty head rather than an acquired-context dependence audit.
- Pixelwise conformal MRI reconstruction uncertainty (2026) produces statistically structured intervals but requires a trained quantile framework; it does not test shared measurement influence between deterministic interpolation contexts.
- Zhang et al. (2019) use learned uncertainty for active MRI measurement acquisition. This is a prospective acquisition-policy direction and is not equivalent to the present retrospective densification analysis.

### Correlated errors and ensemble disagreement

- Classical error propagation, ensemble forecasting, model-discrepancy, and data-assimilation literature already establishes that correlated errors alter uncertainty and spread–error relationships. The identity `||e_a-e_b||² = ||e_a||² + ||e_b||² - 2<e_a,e_b>` is elementary and cannot be claimed as a new theorem.
- Query-by-committee and deep ensembles use prediction disagreement for sample selection or uncertainty. They generally encourage diversity but do not guarantee that members use disjoint physical measurements.

## 3. Novelty that survives the audit

### TMI paper

The defensible contribution is a medical-imaging characterization of **measurement-dependent reliability** in deterministic MRI inter-slice interpolation:

1. separating the elementary correlated-error identity from a task-specific, physically auditable source of correlation—shared acquired slice anchors;
2. intervening on measurement overlap while holding target plane and reconstruction task fixed;
3. showing across fastMRI, IXI, and patient-clustered NingXia that increased sharing raises shared-error fraction and reduces observable disagreement/ranking quality;
4. demonstrating the effect across neural and analytical estimators, multiple endpoints, x2/x4/x6 factors, geometry/intensity controls, complete risk–coverage curves and stable-wrong/benign-diversity failure modes;
5. establishing that disagreement reliability depends on **how prediction diversity is constructed**, not diversity magnitude alone.

This is narrower than “a new theory of ensemble uncertainty” and stronger than “ordinary ensembles sometimes agree while wrong.”

### CVPR paper

The defensible contribution is a mechanism-to-score chain:

1. defining a finite-difference **neural shared-influence** quantity tied to common physical slice anchors;
2. showing that it explains neural error alignment and observable fraction beyond integer overlap count in the larger cohorts, with explicit NingXia heterogeneity under a fixed-count test;
3. experimentally separating local cancellation arrows from the weaker context-level ranking consequence;
4. freezing acquired-anchor leave-one-out residuals as an inexpensive examination difficulty score and testing it against direct differences, output PC, risk–coverage and actual IXI+fastMRI x4→x2 benefit;
5. reporting the negative conclusion that Anchor-CV is not uniquely informative or universally the best ranker, but is computationally distinct because it needs no reconstruction predictions.

The acquired-anchor leave-out operation itself is not novel; its novel role, if accepted, is the frozen deployment-oriented use and its placement in a measurement-dependence analysis.

## 4. Claims rejected or narrowed

- Reject: “first to show that uncertainty/disagreement misses systematic error.” Hu et al. (2020) is a clear precursor.
- Reject: “leave-one-slice-out interpolation is new.” Horvath et al. (2017) used it for evaluation.
- Reject: “Anchor-CV contains information unavailable to adjacent-slice difference.” P6-E06 falsified this.
- Reject: “Anchor-CV is the best MRI interpolation risk score.” Output PC or adjacent MAE wins nAURC in several cohorts.
- Reject: “shared influence universally explains reliability beyond count.” The clean fixed-count NingXia result was null/mixed.
- Reject: “the full chain is causal.” The experiments support local conditional associations; the final context-level ranking arrow is only partially stable.
- Reject: “retrospective densification validates prospective acquisition.” It does not.
- Narrow: “measurement-disjoint is universally superior.” It beats dependence-preserving output scores across all three cohorts, but adjacent-anchor MAE is stronger on NingXia.

## 5. Updated positioning text

Recommended TMI wording:

> Existing MRI uncertainty methods learn uncertainty heads or derive variability from multiple predictions. We study a complementary failure source: deterministic reliability estimates can share the same acquired slices, creating aligned error that cancels in their difference. We identify and intervene on this physical dependence in through-plane MRI interpolation.

Recommended CVPR wording:

> We do not introduce leave-one-slice-out validation or correlated-error algebra. We connect physically shared measurements to local neural influence, quantify when that influence aligns deterministic reconstruction errors, and test a frozen acquired-anchor residual as a low-cost examination difficulty score under strong direct-difference and output-disagreement baselines.

## 6. Policy audit

The official IEEE TMI Instructions to Authors, revision 10.2 (2025-10-09), and the current Submission Checklist both state that initial regular/special-issue submissions are limited to **10 pages, 10-point font or larger, including references**. TMI no longer accepts manuscript-like supplemental documents that extend the paper with text/figures. Therefore:

- the 18–20 page TMI research master is internal only;
- the initial-submission artifact must be independently distilled to at most 10 pages including references;
- the master must not be uploaded as supplemental material.

Source URLs for final verification:

- `https://ieeetmi.org/authors-instructions/`
- `https://ieeetmi.org/submission-checklist/`

## 7. Novelty decision

Proceed with both papers, but with sharply separated claims. The TMI paper has the stronger broad medical-imaging mechanism/generalization contribution. The CVPR paper is viable only if it foregrounds neural shared influence, exact negative boundaries, and the computationally distinct acquired-data score—not Anchor-CV superiority or leave-one-slice-out novelty.
