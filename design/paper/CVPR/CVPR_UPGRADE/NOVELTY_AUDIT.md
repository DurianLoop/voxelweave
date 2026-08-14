# CVPR Upgrade Novelty Audit

Search date: 2026-08-13. Scope: MRI inter-slice interpolation/super-resolution, MRI reconstruction uncertainty, active acquisition, consistency, phase/shifted sampling, and shared-error mechanisms. This is a bounded negative search, not proof that no related work exists.

## Closest verified work

| Work | Same problem? | Same intervention? | Target-preserving overlap manipulation? | Error covariance / observability? | Benefit prediction? | Distinction |
|---|---|---|---|---|---|---|
| Peng et al., *SAINT*, CVPR 2020 | medical slice synthesis; CT experiments | no | no | no | no | spacing-aware synthesis architecture, not reliability-context design. Official: https://openaccess.thecvf.com/content_CVPR_2020/html/Peng_SAINT_Spatially_Aware_Interpolation_NeTwork_for_Medical_Slice_Synthesis_CVPR_2020_paper.html |
| Song et al., *I3Net*, TMI 2024, DOI `10.1109/TMI.2024.3394033` | yes, medical inter/intra-slice interpolation | no | no | no | no | reconstruction architecture exploiting in-plane information; not measurement-overlap reliability. Official record: https://ieeexplore.ieee.org/document/10508991 |
| Greenspan et al., *MRI inter-slice reconstruction using super-resolution*, MRI 2002, DOI `10.1016/S0730-725X(02)00511-8` | MRI inter-slice SR | shifted repeated acquisitions | no same-target reliability contexts | no | no | combines complementary shifted acquisitions to improve resolution, rather than estimating hidden error from disagreement. |
| Nicastro et al., *To shift or to rotate?*, Frontiers in Neuroscience 2022, DOI `10.3389/fnins.2022.1044510` | multi-slice MRI SR | compares acquisition schemes | no | Bayesian accuracy/precision, not disagreement observability | no | optimal design for reconstruction quality, not measurement-sharing-induced consensus blindness. Official: https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2022.1044510/pdf |
| Zhang et al., *Reducing Uncertainty in Undersampled MRI Reconstruction With Active Acquisition*, CVPR 2019 | MRI uncertainty/allocation, but k-space reconstruction | learned next k-space measurement | no | uncertainty-error correlation, not shared-error covariance | yes, learned active acquisition | closest actionable precedent; different inverse problem, intervention, and score. Official: https://openaccess.thecvf.com/content_CVPR_2019/html/Zhang_Reducing_Uncertainty_in_Undersampled_MRI_Reconstruction_With_Active_Acquisition_CVPR_2019_paper.html |
| Küstner et al., *Predictive uncertainty ... deep ensembles*, MRM 2024, DOI `10.1002/mrm.30030` | MRI reconstruction UQ | ensemble/aleatoric model | no | no measurement-overlap chain | no | estimates predictive uncertainty and domain-shift effects; does not diagnose common-mode cancellation by manipulating measurements. PubMed: https://pubmed.ncbi.nlm.nih.gov/38282254/ |
| Remedios et al., *Cycle-Consistent Zero-Shot Through-Plane Super-Resolution*, MICCAI 2025, DOI `10.1007/978-3-031-96628-6_17` | through-plane MRI SR | forward-model cycle consistency | no | posterior ambiguity/cycle consistency, not disagreement-error covariance | no | guarantees data consistency of an SR solution; does not claim agreement certifies correctness or manipulate overlap. PubMed/PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC12805976/ |
| Young et al., *Fully Convolutional Slice-to-Volume Reconstruction for Single-Stack MRI*, CVPR 2024 | single-stack MRI motion/reconstruction | learned slice motion plus interpolation | no | no | no | reconstructs a motion-corrupted stack; does not cross-validate acquired anchors or model common-mode reliability error. Official: https://openaccess.thecvf.com/content/CVPR2024/html/Young_Fully_Convolutional_Slice-to-Volume_Reconstruction_for_Single-Stack_MRI_CVPR_2024_paper.html |
| Savant, *Deep Learning for MRI Slice Interpolation: The Critical Role of Problem Formulation*, arXiv 2026 | MRI slice interpolation | adjacent versus distant input slices | no same-target reliability intervention | no | no | recent non-peer-reviewed collision check; studies reconstruction accuracy, not shared influence or target-free triage. https://arxiv.org/abs/2605.16476 |

## Collision assessment

No reviewed work was verified to combine all of the following:

- deterministic MRI inter-slice interpolation reliability;
- same-target contexts with explicitly controlled measurement overlap;
- the overlap → error covariance/alignment → observable-fraction → ranking chain;
- a deployment-time context partition using only already-acquired through-plane anchors;
- retrospective prediction of x4-to-x2 densification benefit.
- leave-one-acquired-anchor residuals as an examination-level reliability score without x8 inference.

The closest collision risk is the general idea of active MRI acquisition (Zhang et al.) and complementary shifted/rotated multi-slice SR acquisition (Greenspan; Nicastro et al.). Claims must therefore be narrow: novelty is the *error-observability mechanism and acquired-anchor reliability partition*, not the broad ideas of active acquisition, shifted grids, consistency, or uncertainty.

Novelty is rated 4/5, not 5/5, because the audit is bounded and adjacent sampling-design literature is substantial.

The 2026 update search specifically queried acquired-slice leave-one-out validation and through-plane reliability. It found general neuroimaging cross-validation, interpolation-error analysis, and reconstruction UQ, but no verified method matching Anchor-CV's deployment role. This is a bounded negative search, not an exclusivity claim.
