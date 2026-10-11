# Position-channel-only pilot: frozen before CPU inference

Status: post-result, exploratory mechanism diagnostic. Fixed before running the new script. It is not an independent confirmation, a new cohort, or an acquisition-identity intervention.

## Question and fixed sample

In the existing IXI-trained HAT/SwinIR shared-versus-disjoint same-target comparison, how much can changing **only** SwinIR's fourth input channel (the relative z-position map) change the paired-error observability `O`? Use the first three records in `literature/msvalid_geometry_qualification.json` (P1, P2, P3) and the first three eligible records in `literature/remind_native_t2_qualification.json` (ReMIND-003, -007, -009). Score every previously eligible residue-1 and residue-3 target for those patients. No replacement after a failure.

## Intervention and checks

For each target, use the existing phase-0 HAT prediction `a`, phase-0 SwinIR prediction `b0`, phase-2 SwinIR prediction `b2`, target `y`, phase-0 acquired-only support, phase-specific original normalization and unchanged model checkpoints. Construct `bmap` with phase-0 SwinIR left/right images, phase-0 coarse linear image, phase-0 normalization and output coarse image, while replacing only channel 4's constant `rel0` map with `rel2`. The four conditions use the same target and support. Thus `bmap` must use the **original** coarse image even though its map says the other phase's relative position. Check all other input channels are byte-identical and the relative-position maps differ. This is an intentionally out-of-contract input perturbation, not a plausible alternative acquisition.

For each target compute `O(a,b0)`, `O(a,bmap)`, and `O(a,b2)` with the established denominator `T=(MSE(a,y)+MSE(b,y))/2`. Report `O_map-O_shared`, `O_disjoint-O_shared`, companion MAE changes and `abs(O_map-O_shared)/abs(O_disjoint-O_shared)` only when the denominator is nonzero. Aggregate by averaging each residue within patient, then patients within source. Report every target and patient, with no significance interval on this tiny selected pilot. Check the recomputed original shared/disjoint observables, HAT MAE and support size against the existing frozen per-target CSV at `1e-5` absolute tolerance. A check failure is recorded as a failure, never silently omitted.

Read only the fixed public MSValid/ReMIND images and existing checkpoints on CPU float32 with two torch threads and one interop thread. Validate source and checkpoint hashes as in the parent scripts. Refuse to overwrite the pilot output directory. Do not read the locked test split, use CUDA, stop other processes, or change the parent outputs.

Interpretation: a small position-only effect would limit this channel as an explanation of the large full context contrast; a large effect would show input encoding sensitivity. Neither direction separates neighbor content, geometry, normalization, publication processing, or true acquisition identity. The pilot is selected after seeing the main results and cannot support a new inferential claim.
