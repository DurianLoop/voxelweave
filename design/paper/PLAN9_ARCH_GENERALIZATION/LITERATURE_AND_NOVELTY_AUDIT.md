# Plan-9 literature and novelty audit

Audit date: 2026-08-14. Search scope: MRI/medical inter-slice interpolation, architecture-diverse volumetric super-resolution, deterministic reconstruction uncertainty, and physical-measurement dependence. Primary venue/publisher records were preferred.

## Architecture references and implementation boundary

| Family | Primary work | What the publication establishes | What the local experiment actually uses |
|---|---|---|---|
| Spatially aware synthesis | [SAINT, CVPR 2020](https://openaccess.thecvf.com/content_CVPR_2020/html/Peng_SAINT_Spatially_Aware_Interpolation_NeTwork_for_Medical_Slice_Synthesis_CVPR_2020_paper.html) | Spatially aware medical slice synthesis with arbitrary upsampling support | Adapted local SAINT-style conditional CNN, locally trained on fastMRI; not official weights or an exact official reproduction |
| Dedicated inter/intra-slice network | [I3Net, IEEE TMI 2024](https://ieeexplore.ieee.org/document/10508991/) | Cross-view inter/intra-slice modeling for medical slice synthesis | Official architecture lineage, locally retrained checkpoints; no official weights |
| Implicit coordinate reconstruction | [CycleINR, CVPR 2024](https://openaccess.thecvf.com/content/CVPR2024/html/Fang_CycleINR_Cycle_Implicit_Neural_Representation_for_Arbitrary-Scale_Volumetric_Super-Resolution_of_CVPR_2024_paper.html) | Continuous coordinate-based volumetric super-resolution with cycle consistency and local attention | Internal CycleINR-style reproduction using the local ArSSRNet backbone and cycle loss; not the exact official model |
| Clinical MRI super-resolution precedent | [DeepResolve, Radiology 2018](https://pubmed.ncbi.nlm.nih.gov/29582464/) | Thin-slice knee MRI reconstruction assessed quantitatively and by readers | Literature context only; no recovered compatible checkpoint |
| MRI uncertainty/QC | [Aleatoric uncertainty in accelerated prostate MRI, 2026](https://pubmed.ncbi.nlm.nih.gov/42192056/) | Acquisition perturbation variance can correlate only moderately with slice error and can reflect acquisition fragility | Related uncertainty boundary; it does not manipulate shared physical anchors for the same missing interpolation target |

## Nearest-concept matrix

| Work family | Same missing physical target held fixed? | Physical measurement identity manipulated? | Error alignment/cancellation measured? | Local shared measurement influence measured? | Cross-architecture falsification? |
|---|---:|---:|---:|---:|---:|
| SAINT / I3Net / CycleINR reconstruction papers | No reliability intervention | No | No | No | Reconstruction comparisons only |
| MRI probabilistic/ensemble uncertainty | Usually no | Usually no | Rarely/systematic error discussed | No physical-anchor response definition | Often multiple uncertainty methods, not this mechanism |
| Classical through-plane interpolation analyses | Sometimes synthetic targets | Sampling geometry, not paired reliability contexts | No | Analytical coefficients possible but not linked to disagreement blindness | Analytical only |
| Plan-9 study | Yes | Yes | Yes | Yes, with a frozen stability gate | Yes: transformer, dedicated CNN, spatial conditional CNN, implicit-coordinate reproduction |

## Novelty verdict after architecture falsification

The defensible novelty remains scoped: a same-target physical-measurement intervention links deterministic estimator dependence to error alignment and disagreement observability. Plan 9 strengthens the phenomenon claim because all five evaluated neural architectures show greater observable error under disjoint physical contexts. It does **not** justify either of the following broader claims:

- “influence always outperforms anchor count”: SAINT's broad-grid advantage is small/uncertain, and I3Net/CycleINR fail the frozen influence-stability gate;
- “disjoint contexts always improve examination ranking”: SAINT is slightly negative and I3Net is null within uncertainty, while CycleINR is strongly positive.

The new result therefore narrows the mechanism statement to: physical measurement dependence robustly changes local error geometry across the evaluated paradigms; the magnitude, finite-response stability, and downstream ranking benefit are architecture dependent.

No “first” claim is recommended. No exact-official-reproduction wording is permitted for the adapted SAINT or CycleINR-style branches.

