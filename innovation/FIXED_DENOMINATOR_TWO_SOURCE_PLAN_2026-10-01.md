# Two-source fixed-denominator sensitivity: rule frozen before calculation

**Status:** Post-main-result algebraic sensitivity analysis, not a new patient experiment. The original MSValid and ReMIND positive context results and the ReMIND cosine decomposition are known. This plan is frozen before computing the results below. No images, model weights, target pixels, GPU or locked test data will be read; only the original per-target CSVs and summaries are inputs.

## Question

Could the large `Delta O` arise mainly because each condition divides disagreement by a different companion-dependent paired MSE? Keep the *shared-context paired MSE* as the common denominator for the same target:

`Q_s = D_s / (4 T_s) = O_s`, `Q_d = D_d / (4 T_s) = O_d * T_d / T_s`, and `Delta Q = Q_d - Q_s`.

Here `D` is mean squared output disagreement on the existing fixed acquired-only mask, and `T` is paired MSE against the same withheld target. Use the stored per-target `shared_observable`, `disjoint_observable`, `shared_paired_mse`, `disjoint_paired_mse`; for ReMIND also cross-check stored `shared_disagreement_mse` and `disjoint_disagreement_mse`. MSValid's `D` is reconstructed algebraically from `4*T*O`. All `T` must be finite and strictly positive. This fixed denominator is still **oracle/retrospective** because `T_s` uses the target; it is not a deployable reliability score.

## Frozen complete-cohort analysis

Require source CSV SHA-256, exact unique patient/target membership and row counts from original summaries: MSValid 84 patients/479 targets, ReMIND 62 patients/248 targets, each patient with residue 1 and 3. Cross-check that patient-weighted original `Delta O` reproduces the original summaries before interpreting `Delta Q`. Average targets within residue, the two residues equally within patient, then patients equally. Report `Q_s`, `Q_d`, `Delta Q`, `Delta Q - Delta O`, positive/negative patient counts and the target-level sign count. Report both sources regardless of direction and the two ReMIND protocol groups without calling them independent confirmations.

Use 5,000 patient-bootstrap percentile draws and the original analysis seeds (`20261001` MSValid; `20261002` ReMIND). For ReMIND draw within ordinary T2 and BLADE separately, then weight by completed group counts 35/62 and 27/62. These are exploratory post-result intervals conditional on the chosen cohorts and model pair, not an adjustment for research-selection history. Check all finite values, reconstructed `D`, exact original patient means/summary, strata membership and zero failure. Write a new result directory without overwriting original inputs.

If `Delta Q` stays large and positive, varying `O`'s denominator is not the sole explanation. If it shrinks, state the amount without treating `Delta O - Delta Q` as a causal mechanism contribution. This exercise cannot separate anatomy, signed geometry, original acquisition identity or publication processing; the native-linear control already shows the phenomenon is not learned-pair-specific.
