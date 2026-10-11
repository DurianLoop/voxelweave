# Plan 4 Literature and Novelty Audit

## Scope and search result

The audit covered classical interpolation error, anisotropic medical slice synthesis, video-frame interpolation ambiguity, inverse-problem uncertainty, MRI data consistency, posterior sampling, and alternative sampling lattices. Searches were run on 2026-08-13 and prioritized primary papers/proceedings.

## Closest intellectual neighbors

1. Classical approximation theory relates interpolation error to smoothness/derivatives and grid spacing. This motivates—but does not establish for neural reconstruction—the curvature–spacing tests. Lucas analyzes derivative approximation and error bounds for cubic splines ([SIAM J. Numerical Analysis](https://epubs.siam.org/doi/10.1137/0711049)).
2. Deep medical slice synthesis improves reconstruction architectures. MSR synthesizes anisotropic brain MRI using marginal super-resolution and fusion ([Peng et al.](https://arxiv.org/abs/1908.05599)); SAINT addresses spatially aware slice synthesis ([Peng et al.](https://arxiv.org/abs/2001.00704)); I³Net models inter-/intra-slice information ([Wang et al.](https://arxiv.org/abs/2405.02857)). These works do not, in the reviewed material, study agreement blindness as a function of shared acquired slices.
3. Video interpolation recognizes non-unique intermediate motion and averaged deterministic solutions ([Zhou et al., CVPR 2023](https://openaccess.thecvf.com/content/CVPR2023/html/Zhou_Exploring_Motion_Ambiguity_and_Alignment_for_High-Quality_Video_Frame_Interpolation_CVPR_2023_paper.html)), and degradation with larger temporal gaps ([Argaw & Kweon, CVPR 2022](https://openaccess.thecvf.com/content/CVPR2022/html/Argaw_Long-Term_Video_Frame_Interpolation_via_Feature_Propagation_CVPR_2022_paper.html)). This supports the ambiguity/spacing motivation but does not provide the controlled overlap intervention.
4. MRI reconstruction consistency methods enforce agreement with acquired measurements or learned calibration relations, e.g. SPIRiT ([Lustig & Pauly](https://pmc.ncbi.nlm.nih.gov/articles/PMC2925465/)). Posterior-sampling methods instead represent multiple acquisition-consistent reconstructions ([Edupuganti et al.](https://arxiv.org/abs/2010.00042)). Both differ from using two target-preserving, measurement-disjoint contexts to diagnose shared deterministic failure.
5. Training-free inverse-problem uncertainty has also been studied directly ([Zhang et al., WACV 2024](https://openaccess.thecvf.com/content/WACV2024/papers/Zhang_On_the_Quantification_of_Image_Reconstruction_Uncertainty_Without_Training_Data_WACV_2024_paper.pdf)). The current contribution is narrower: it experimentally isolates shared-information overlap as a determinant of disagreement observability.

## Novelty statement

Within this search, no direct prior work was found that simultaneously:

- holds the missing physical target fixed;
- varies overlap of acquired context from zero to maximal;
- measures the resulting ability of disagreement to reveal deterministic consensus error;
- and validates the predicted effect across neural and analytical interpolators and independent MRI cohorts.

This is a bounded literature conclusion, not proof that no paper exists. The safest central novelty is the controlled diagnostic principle and benchmark protocol, not the classical curvature relation or the general fact that interpolation is ambiguous.

## Literature-driven experiments

- Classical error theory motivated the acquired-anchor second-difference × spacing² feature. It improved a held-out fastMRI regression beyond spacing alone, but was not a universally superior univariate proxy; this prevents an overclaimed “law.”
- Video ambiguity work motivated the conditional-central-tendency explanation and the expectation that multiple deterministic models can agree on an averaged error.
- MRI consistency literature motivated separating measurement consistency from error observability. The overlap intervention changes which measurements support the estimate rather than merely applying an image transform.

