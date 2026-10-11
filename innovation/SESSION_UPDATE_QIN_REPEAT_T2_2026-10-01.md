# MRI innovation continuation: QIN full repeat-source audit

## User request and work boundary

The user requested continued paper reading and novelty assessment grounded in prior MRI work, with immediately testable ideas explored, deferred ideas recorded, and all conversation products retained under `D:/MRI/innovation`. The existing GPU is occupied by a separate IXI run. This continuation used CPU and official, public TCIA technical headers only. It did not start training, access locked IXI test images, decode QIN PixelData, or change the running experiment. Patient images and the 30 downloaded DICOM ZIPs stay in the git-ignored `innovation/data/qin_prostate_repeat_t2/` directory.

## Completed source test

The [QIN first-patient pilot](QIN_REPEAT_T2_HEADER_PILOT_PLAN_2026-10-01.md) motivated a [frozen full-cohort header screen](QIN_REPEAT_T2_ALL_HEADER_PLAN_2026-10-01.md). The 15/15-pair run finished with 30/30 series downloaded or reused, zero download/parse failures, and **zero strictly same-plane pairs**. All 15 fail orientation and position-grid/plane-count checks; five differ in TR, one in TE and two in pixel spacing. The complete [result](QIN_REPEAT_T2_ALL_HEADER_RESULT_2026-10-01.md) links raw metrics and the official source inventory. An independent [read-only verifier](experiments/verify_qin_repeat_t2_all_headers.py) checked all 30 ZIP SHA-256 values, source and script hashes, every technical header and the failure conditions. It also corrected a metric-label error: archived "center" positions were DICOM first-pixel positions. True field-of-view centers still fail all eight pairs with equal layer counts. No pixel experiment follows from this source gate.

## Paper evidence applied to the innovation choice

The local archive currently registers 27 primary PDFs plus source snapshots and reading notes. This continuation reused the already archived bounded full-text checks rather than counting titles as new evidence:

| Candidate | Closest archived paper constraint | Local experimental status and next decision |
|---|---|---|
| Same-target, shared/disjoint published-slice context audit | Hu 2021 and MRI uncertainty work already cover error prediction; [Lee/Choi and Bhutto](literature/2026-10-01_shared_context_neighbours_fulltext.md) constrain broad measurement-audit and perturbation-score claims. | Same IXI-trained HAT/SwinIR pair has positive `Delta O` on MSValid and ReMIND; the [linear-partner control](PUBLIC_LINEAR_PARTNER_CONTROL_RESULT_2026-10-01.md) is also strongly positive. Keep only the bounded retrospective context contrast, report confounding and negative deployability results, and finish the [publication gate](CLAIM_PUBLICATION_GATE_2026-09-30.md). This is the strongest evidence-backed manuscript candidate, not a new reconstruction model. |
| Pure independent acquisition-plane identity | Current QIN source has real repeat-acquisition dates and 2D original/primary headers, but 0/15 pairs meet exact-plane geometry. Local fastMRI candidates lack documented independent timing and precise source rights. | **Source gate fails.** Seek another licensed, documented source with matched physical planes; freeze analysis before target pixels. Do not call registered rescan differences a pure identity effect. |
| Profile-aware forward-model identification | [SMORE, Remedios, ESPRESO and SPTSR](literature/2026-09-30_slice_profile_prior_art.md) already separate thickness/spacing or estimate profiles. | The [known-profile held-out pilot](KNOWN_PROFILE_HOLDOUT_PILOT_RESULT_2026-10-01.md) selected the correct kernel 5/12 times and improved missing-layer MSE over the fixed kernel 0/12 times. Stop this selection rule. A fresh, credible thin-reference source and independently frozen estimator/baselines are prerequisites for a new method claim. |
| Arbitrary offset diffusion, frequency branches or local action gates | [HiFi-Diff/I3Net/CRIS](literature/2026-09-30_interpolation_prior_art.md) and [DRIFT/PDM](literature/2026-09-30_diffusion_prior_art.md) already occupy the broad method space. | Existing local geometry, wavelet and selector tests show marginal or negative benefits; [target-error ranking](TWO_SOURCE_TARGET_ERROR_RANKING_RESULT_2026-10-01.md) is not consistently improved across both external sources. Do not start another GPU model or advertise clinical risk selection from these records. |

The paper checks are bounded, not a final exhaustive novelty search. The broad OpenAlex query [screen](literature/2026-10-01_context_overlap_openalex_result.md) had poor relevant-paper recall. A target-venue literature refresh and source/license/author review remain necessary before external submission.

## Preserved next steps

1. The public-only MIRA draft remains a retrospective **published-slice context** audit. Keep ReMIND `MPR`, phase/geometry/content covariation, same-cohort follow-up analyses, linear-partner negative control and deployable-score negative results visible. Do not add QIN prostate data to the brain manuscript.
2. For an acquisition-identity claim, identify a lawful brain repeat series with independent acquisition evidence and physically matched planes. Freeze source IDs, field-of-view center calculations, protocol/position tolerances, target definition, failures and patient statistics before reading target pixels. If no such source exists, leave the claim unmade.
3. For a different forward-model paper, first secure a credible thin-response reference and predefine a test that makes wrong profiles fail on truly held-out measurements while improving missing-plane error relative to fixed-profile and ESPRESO-like baselines. The current three-patient training-only pilot cannot support this claim.
4. Recheck the source and release obligations, actual reproducible environment, authorship and target-venue literature before treating the internal manuscript as a submission package.

## Verification

Run `D:/conda/envs/MRI/python.exe -B innovation/experiments/verify_qin_repeat_t2_all_headers.py` for the independent nonpixel source check, then `D:/conda/envs/MRI/python.exe -B innovation/verify_archive.py` for the literature manifest and local Markdown links. The frozen primary screen should not be rerun in place because it intentionally refuses to overwrite its result.
