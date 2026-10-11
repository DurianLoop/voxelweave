# MSValid IXI-trained HAT/SwinIR secondary replication: frozen before inference

Status: result-after-designed secondary analysis. This protocol was fixed after the fastMRI-trained HAT/SwinIR MSValid result and after the response-influence negative result, but before running the IXI-trained model pair on MSValid. It is not a new patient cohort, a second prespecified external confirmation, or an intervention that isolates training-source effects.

## Scientific question and decision

Can the same shared-versus-disjoint paired-error observability phenomenon be reproduced on the same public MSValid RRMS T2 patients using a frozen HAT/SwinIR pair trained on public IXI T2, rather than the previously used fastMRI-trained pair? If positive, it broadens the observed frozen-model-pair coverage and gives a public-training-source route for a future rights-conscious manuscript. If null or negative, the finding remains specific to tested weights and the negative result is retained.

The single primary contrast is patient-weighted `O_disjoint - O_shared` for IXI-trained HAT phase 0 as fixed reference and IXI-trained SwinIR phase 0 versus phase 2 as companion. `O=mean(((a-b)/2)^2)/T`, `T=(MSE(a,y)+MSE(b,y))/2` on the acquired-only support. Each patient's residue-1 and residue-3 target means receive equal weight, then 84 patients receive equal weight. Report the two `O` means, delta, 5,000-draw paired patient-bootstrap percentile 95% interval with seed 20261001, positive/negative patient counts, and companion MAE by condition. The declared criterion for a positive secondary replication is at least 70 fully scored patients and a strictly positive interval lower bound; no fallback cohort, mask, endpoint or checkpoint will be selected after seeing results. Even if positive, no claim of independence from the earlier MSValid test or proof of anchor-ID-only causality is allowed.

## Frozen inputs and inference

- Geometry-qualified 84 patients / 479 residue-1/3 targets from `literature/msvalid_geometry_qualification.json`; source images are the first T2 volume per patient at `data/msvalid_first_t2/P*.nii.gz` and must match the existing integrity manifest. Native z spacing is 3--6 mm; x4 is retrospective subsampling of native planes, not thin-slice reference recovery.
- IXI HAT: `baseline/ixi_hat_2p5d/runs/full_test115/checkpoints/hat_epoch_best.pth`, SHA-256 `2FAE831AB933CF260972260EBEC4349F3895106AC7B4D1AF3BA368F407498EAE`.
- IXI SwinIR: `baseline/ixi_swinir_2p5d/runs/full/checkpoints/swinir_epoch_best.pth`, SHA-256 `6A819E47E65BD96C2D6E5B6D3ADC212E1A46347080A0A661C602367BE8A6F323`.
- Use the existing IXI `HAT2p5DInterpolator` and `SwinIR2p5DInterpolator` classes, CPU float32 with two torch threads, and the same `normalize_volume`, 256x256 interpolation, per-phase observed-only min/max, acquired-only 1%-threshold foreground support, geometry, target order and per-target metrics as `experiments/msvalid_mira_confirmation.py`.
- Run the independently copied script at `experiments/msvalid_ixi_weights_secondary.py`; refuse overwrite of `experiments/msvalid_ixi_weights_secondary/`. Validate checkpoint hashes, source geometry and nonfinite/empty supports. Record protocol/script/qualification/checkpoint SHA-256 and all patient/target rows. Do not access GPU.

## Interpretation boundaries

This is post-result model-pair replication on a reused external source. The MSValid patients have already contributed to the original endpoint, and both IXI checkpoints differ in training data and potentially other implementation details from the fastMRI checkpoints. A positive result adds breadth but cannot be pooled with the prior prespecified interval as if two independent trials occurred. Phase 2 changes full slice content, signed geometry and per-phase normalization along with anchor overlap. The result does not establish a deployable correctness score, lesion safety, true thick-to-thin MRI super-resolution or legal rights to share copied data/images.
