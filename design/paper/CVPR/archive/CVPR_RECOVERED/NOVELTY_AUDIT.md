# Refined Novelty Audit: Shared Influence and Disagreement Reliability

Audit date: 2026-08-14. This is a bounded literature audit, not an absolute priority claim.

## Refined claim

The novelty claim is not the error-difference identity, consensus blindness in general, ensemble diversity, MRI uncertainty, or leave-one-slice-out interpolation. It is the combined empirical program that:

1. preserves one missing physical target while manipulating dependence among the acquired slice measurements used to reconstruct it;
2. measures how that dependence aligns target errors and cancels them in output disagreement;
3. falsifies integer overlap as a sufficient monotone dose;
4. replaces it with analytical coefficient influence and a local neural finite-response influence approximation; and
5. connects the mechanism to an acquired-only examination-level triage consequence while retaining non-superiority and prospective-use boundaries.

## Closest families

| Literature family / representative work | What it establishes | Physical dependence manipulated? | Same missing target preserved? | Error cancellation measured? | Shared influence quantified? | Reliability observability linked? |
|---|---|---:|---:|---:|---:|---:|
| Deep ensembles and diversity (Lakshminarayanan et al.; Ortega et al.) | Predictive diversity and ensemble error/generalization | No | No | Algebraically related, not this intervention | No physical-measurement influence | Not in MRI interpolation |
| MRI Bayesian/ensemble UQ (Edupuganti et al.; Narnhofer et al.; Küstner et al.; Luo et al.) | Posterior/ensemble uncertainty for undersampled MRI | Sampling operator may vary, but dependence between paired reliability contexts is not isolated | No | No | No | Error–uncertainty association, not common-measurement cancellation |
| Training-free inverse-problem UQ (Zhang et al., WACV 2024) | Approximate posterior without training data | No paired dependence intervention | No | No | No | Uncertainty estimation, not observability under dependence |
| Systematic MRI error prediction (Hu et al.) | Uncertainty can miss systematic reconstruction errors | No | No | Shows the blind spot | No | Yes, but without the physical mechanism tested here |
| MRI self-consistency / SPIRiT | Compatibility with acquired measurements | Measurement consistency is central | No paired same-target reliability comparison | No | No | No |
| Active MRI acquisition (Zhang et al.) | Select measurements to reduce uncertainty | Acquisition changes | Not the same controlled missing target | No | No | Optimization rather than mechanism isolation |
| Slice interpolation / leave-one-slice-out (SAINT; I3Net; Horvath et al.) | Reconstruction and held-out-slice checks | No dependence ladder | Sometimes | No | No | No |
| Shifted multi-slice SR / acquisition design (Greenspan et al.; Nicastro et al.) | Complementary shifted measurements improve reconstruction | Yes, for accuracy/precision | Not as a paired reliability intervention | No | No | No |

## Collision judgment

No audited work was found that jointly performs all five distinguishing operations: same-target physical-dependence control, target-error alignment measurement, disagreement cancellation analysis, influence-beyond-count refinement, and reliability-observability consequence. This supports a scoped novelty statement only.

## Safe manuscript wording

Use: “We study a controlled setting in which the physical measurements generating two deterministic reconstructions can be varied while the missing target is fixed, and show that shared local estimator influence is associated with aligned error and disagreement blindness.”

Avoid: “first,” “proves,” “universal,” “new uncertainty estimator,” or any claim that the elementary decomposition or Anchor-CV operation is novel.

## Remaining novelty risks

- A reviewer may view finite-response cosine as a standard local sensitivity diagnostic. The response is the physical same-anchor pairing and controlled reliability question, not the cosine formula alone.
- The evidence is limited to MRI slice interpolation and two related neural families. Generalization to other inverse problems remains a hypothesis.
- The related TMI paper shares the physical-intervention phenomenon. Submission sequencing and disclosure must establish a distinct contribution and comply with venue policy.
