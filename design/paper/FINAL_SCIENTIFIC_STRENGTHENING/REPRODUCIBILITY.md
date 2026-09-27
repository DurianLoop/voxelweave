# Reproducing the final scientific iteration

The study is retrospective. `FINAL_ITERATION_PROTOCOL.md` binds exactly three new analyses; the initial protocol and both freeze records remain immutable. This directory contains the saved neural predictions and responses needed to reproduce results without training or GPU inference. It is not an untouched-cohort or preregistration claim.

## One-command CPU reproduction

From this directory on the recorded Windows environment:

```powershell
D:/conda/envs/MRI/python.exe -B reproduce_main.py
```

The command reconstructs historical observations from retained prediction/response arrays, reconstructs all three new experiments independently, recomputes clustered statistics, asserts the final LaTeX values, recreates the five figure assets and 54 separate report cards, and writes `REPRODUCTION_CHECK.md`. It neither starts GPU inference nor installs/overwrites a paper. Per-stage logs are under `logs/replay_*.log`; `outputs/reproduction_run.json` records completion. Several minutes of CPU and disk time are required. All arrays must remain available; missing data are errors, never simulated replacements.

`scripts/reproduce_arrays.py` independently retains the historical arithmetic order (float32 subtraction followed by float64 error energies) and uses the old per-observation tables only for frozen keys and assertion targets. `scripts/reproduce_new.py` reconstructs metrics and simultaneous intervals from new arrays. Weighted ranks are verified against explicit repeated-case bootstrap expansion. The historical guard's negative conclusion is replayed from the lowest preserved per-examination score records and the frozen CDF/threshold parameters; a full raw-image replay of every old exploratory score or supplemental benchmark is not claimed.

## Input and output boundaries

- `source_manifest.json`: frozen original data, predictions, 26 used checkpoints, code and historical observations. Candidate checkpoint availability is not checkpoint usage.
- `prepared_input_manifest.json`: target files and acquired-only pools/support/scales; physically separate input and target paths.
- `outputs/phase_arrays`: legacy and corrected physical-coordinate predictions, including phase-0 wrapper checks.
- `outputs/acquired_responses`: target-free response formation; metadata is committed before the separate target is opened.
- `outputs/proposition_arrays`: fixed-context neural outputs for every field and amplitude; no target access.
- `outputs/legacy_control_arrays`, `outputs/legacy_influence_arrays`: regenerated historical inputs for exact numerical reproduction.
- `outputs/array_bindings_all.json`, `outputs/new_array_bindings.json`: hashes of every array read by the independent reproduction.
- `original_snapshot`: exact original CVPR/TMI files and entry documents. TMI is outside the scientific scope of this final iteration.

Scientific output CSVs are comparisons, not substitute data. NA remains NA. No missing score is replaced with zero and no response association is borrowed across information contracts. The original six-stratum HAT/SwinIR stability gate is NA in the new two-cohort experiment; only its existing per-stratum criterion applies.

## MIRA API and report cards

`scripts/mira.py` accepts `audit_pair(estimator, context_a, context_b, target_location, amplitude=..., estimator_b=...)`. A missing `estimator_b` uses the same callable. Context keys are physical anchor IDs. Wrappers must freeze weights, evaluation mode, preprocessing, clipping and support provenance. A provenance flag is a declared contract, not a security guarantee. This generic NumPy interface demonstrates estimator dispatch and embedded responses; the model-matched experimental wrappers are in `acquired_probe.py` and the preserved inference scripts.

`scripts/build_report_cards.py` writes seven separate scientific fields with design-specific intervals and explicit eligibility. It never combines them into a scalar reliability score. Cross-architecture rows have no registered cross-architecture finite-response probe, so their influence/stability fields remain NA. Acquired-only influence rows do not inherit phase-ranking results.

## LaTeX and visual assets

```powershell
D:/conda/envs/MRI/python.exe -B scripts/build.py
D:/conda/envs/MRI/python.exe -B scripts/render.py
```

The build targets only `revised_manuscript/main.tex` and `revised_manuscript/supplement.tex`, using the existing CVPR template and MiKTeX/pdflatex/BibTeX. Local MiKTeX user configuration and Poppler execution may require the same outside-workspace runtime access used by the completed build. This is an environment permission requirement, not a missing scientific input. No network service or paid generation is required. Figures use saved real MRI arrays or quantitative results; no generated anatomy is used.

`scripts/revise_manuscript.py` and `scripts/revise_supplement.py` recreate the review copy from the frozen originals. `scripts/install_final.py` is a separate guarded installation step; it refuses unrecognized changes and requires all reproduction/build checks. Run `scripts/protection_audit.py --after-install` to verify snapshots, unchanged TMI files, original scientific inputs and prepared data. Full package and environment inventories are in the final delivery audit.

## Limits

Bootstrap intervals cover their declared within-iteration families, not retrospective selection uncertainty. Error evaluation requires targets even when influence formation is acquired-only. No clinical/prospective/general-vision or calibrated acceptance-probability claim is made. The scientific search stops after the three registered analyses.
