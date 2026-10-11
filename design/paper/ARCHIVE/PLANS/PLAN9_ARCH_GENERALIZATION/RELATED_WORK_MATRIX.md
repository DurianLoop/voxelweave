# Plan-9 related-work matrix

| Work | Primary source | Main object | Same target / physical-context intervention | Reliability mechanism overlap |
|---|---|---|---|---|
| SAINT | [CVPR 2020](https://openaccess.thecvf.com/content_CVPR_2020/html/Peng_SAINT_Spatially_Aware_Interpolation_NeTwork_for_Medical_Slice_Synthesis_CVPR_2020_paper.html) | Spatially aware medical slice synthesis | No | None; reconstruction method only |
| I3Net | [IEEE TMI 2024](https://ieeexplore.ieee.org/document/10508991/) | Inter/intra-slice synthesis | No | None; reconstruction method only |
| CycleINR | [CVPR 2024](https://openaccess.thecvf.com/content/CVPR2024/html/Fang_CycleINR_Cycle_Implicit_Neural_Representation_for_Arbitrary-Scale_Volumetric_Super-Resolution_of_CVPR_2024_paper.html) | Arbitrary-scale implicit volumetric SR | No | Slice consistency is a reconstruction goal, not disagreement reliability or error cancellation |
| DeepResolve | [Radiology 2018](https://pubmed.ncbi.nlm.nih.gov/29582464/) | Thin-slice knee MRI SR with reader evaluation | No paired reliability context | Clinical reconstruction precedent only |
| Prostate MRI aleatoric UQ | [PubMed 2026](https://pubmed.ncbi.nlm.nih.gov/42192056/) | Acquisition-perturbation variance | No same missing interpolation target | Related acquisition fragility; no shared-anchor influence |
| Plan-9 study | Local frozen protocols | Deterministic disagreement observability | Yes | Measures physical dependence, error alignment/cancellation, stable local influence and its failures |

The detailed novelty decision is in `NOVELTY_AUDIT.md`; implementation provenance is in `BASELINE_RECOVERY_AUDIT.md`.

