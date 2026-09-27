# Research audit and inventories

This file carries inventory/provenance detail removed from the scientific narrative. Exact paths and hashes are authoritative in the associated JSON/CSV files, not in a rounded count quoted in prose.

## Freeze

- `original_manifest.json`: 170 original paper/entry-document files, with root-relative copies in `original_snapshot`.
- `source_manifest.json`: 2,524 used source assets, including 26 used checkpoints, predictions, targets, model/preprocessing code and historical evidence observations.
- `prepared_input_manifest.json`: 973 prepared inputs/targets with acquired support/scale and target access separated.
- Protocol execution SHA-256: `dd90cfa52cc35937dd08571897fd1a99509632b23335825527692243667e99db`.
- `freeze.json` binds the initial protocol and registries; `execution_freeze.json` binds the documented pre-inference coordinate correction. `FINAL_ITERATION_PROTOCOL_V1.md` preserves the exact initial bytes.

The inherited Plan17 research ledger separately cataloged 1,623 paper source files, 832 CSV files, 64 split files, 1,336 available checkpoint candidates and 655 training configurations. Those are inventories of different scopes, not independent experiments or a statement that every available candidate checkpoint was used. The present iteration hashes all 26 checkpoints involved in the evidence it reproduces; it does not claim to have used or rehashed every unrelated training candidate in the workspace. The full inherited ledger remains at `../PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK`.

## Retained new arrays

| Array group | NPZ files | Role |
|---|---:|---|
| phase_arrays | 695 | Five-model, two-cohort phase outputs; legacy and corrected-coordinate variants distinguished |
| acquired_responses | 834 | Two-model, two-cohort, three-target finite responses at every amplitude |
| proposition_arrays | 24 | Twelve IXI cases × two models, every comparator/field/amplitude |
| legacy_control_arrays | 322 | Historical three-cohort HAT/SwinIR control reproduction |
| legacy_influence_arrays | 966 | Historical three-target influence reproduction |

`outputs/array_inventory.json` records exact byte counts. `outputs/array_bindings_all.json` and `outputs/new_array_bindings.json` bind every array actually read by reproduction. Arrays are retained locally and are intentionally excluded from the lightweight review ZIP, which is not a standalone raw-data distribution.

## Chronology and failures

`logs/events.jsonl` records actual inference starts/completions and script hashes. Initial and amended protocol timing is preserved. Source inspection and coordinate correction preceded new inference; the whole research project remains retrospective. An unsuccessful first reproduction run encountered an observation-key naming difference; its corrected full replay passed. Build logs retain sandbox configuration failures and the successful permitted MiKTeX/Poppler runs.

No new untouched cohort was authenticated. No fourth scientific analysis or new scalar scoring family was opened. GPU inference finished before the final CPU reproduction and paper editing. Concurrent unrelated workspace GPU work was not stopped or modified.

## Final integrity

`outputs/protection_before_install.json` and `outputs/protection_after_install.json` record snapshot, source and input checks. `outputs/installed_files.json` lists each intentional CVPR replacement with before/after hashes. TMI and scientific input assets remain unchanged. `outputs/environment.json` contains actual package versions; `build_logs/build_audit.json` and the page-render audit record final document checks.
