# Known-profile held-out-observation pilot: frozen before pixel analysis

**Status:** training-only synthetic, CPU pilot. This tests a proposed falsification route, not a trained MRI method, real acquisition profile estimate, independent external confirmation or clinical thick-to-thin recovery.

## Fixed patients and factorial

Use exactly the first three case IDs in `dataset/IXI/splits/seed3407/train_cases.txt`: IXI013, IXI015 and IXI017, each one's unique `dataset/IXI/raw/T2/IXI*-T2.nii.gz`. Assert none occurs in val/test case lists. No replacement on load or geometry failure. Read only these train T2 volumes. Downsample each native x-y plane to 32 x 32 by `skimage.transform.resize(..., anti_aliasing=True, preserve_range=True)` and retain native z order. Normalize by the maximum absolute intensity of the **simulated acquired anchors** for each condition, applying the same factor to latent target planes; do not use target extrema.

Four known synthetic forward conditions per patient: true through-plane Gaussian `sigma_z ∈ {0, 1.5}` native layers and anchor center stride `s ∈ {4, 6}` native layers, phase 0. `sigma=0` is an identity kernel; positive sigma uses `scipy.ndimage.gaussian_filter1d(mode="reflect")`. These are simulated kernels on already acquired native-response images, not measured slice-selection profiles. Retain anchors at `0,s,2s,...`; every third anchor starting from the second is a held-out **observed** layer. Candidate assumed kernels are `sigma ∈ {0,1.5,3.0}`. All candidates use the same fit anchors and heldout anchors within each condition.

## Fixed linear inverse and scoring

For a candidate kernel matrix `G_sigma` and fit-anchor selection `P_fit`, solve independently per x-y pixel

`argmin_x ||P_fit G_sigma x - y_fit||² + 0.03 ||D2 x||² + 1e-5 ||x||²`, 

where `D2` is the z second-difference matrix. Use one Cholesky factorization per candidate and all 32x32 pixels as right-hand sides. Predict the heldout acquired planes with `P_hold G_sigma x_hat`, select minimum heldout MSE (ties to smaller sigma), and then **refit on every acquired anchor** under the selected candidate before measuring MSE against latent native-response planes whose index is not an anchor. Also refit each candidate to report candidate target MSE, the true-kernel candidate, fixed sigma-0 baseline and oracle candidate selected by target truth (diagnostic only). The selected method may use heldout observation values for final refit; they are not target-layer truth.

Use one foreground support per condition: pixels whose mean absolute acquired-anchor value exceeds 5% of the maximum of that map. Hold it fixed across candidates and z positions; fail on an empty mask. Score heldout MSE on every heldout anchor and target MSE on every native nonanchor layer, then average over included pixels/layers. Report each patient's four conditions, per-candidate heldout/target errors, selected kernel, true kernel, fixed/default and oracle target errors, selected-minus-fixed target error, and all failures. Do not compute a confirmatory p-value or optimize ridge/holdout pattern/sigma set after seeing results.

## Decision boundary

If heldout-selected candidates repeatedly harm missing-layer error relative to fixed sigma 0, the proposed observation-based profile gate fails this pilot; retain all conditions. If they help, the result is only a training-patient feasibility signal. Before a publication claim, qualify an independent high-resolution/reference source and a physically defensible profile family, freeze more patients and unseen kernel/spacing combinations, compare ESPRESO or another actual kernel-estimation baseline and a supervised error predictor at the same observation budget, and verify that fewer fit anchors did not alone determine the ranking. No GPU or locked IXI test split is involved.
