# Frozen IXI x2 Evaluation

Freeze time: 2026-08-13, before any x2 test reconstruction or metric existed.

## Purpose

Generate the definition-matched IXI x2 endpoint needed to test frozen x4→x2 retrospective densification benefit on the 115-case IXI cohort. This is a consequence test, not model selection on test performance.

## Frozen checkpoint selection

Candidate completed checkpoints were inspected only through training/validation records:

- `full_test115_x2`: best recorded validation loss approximately `0.030423`; SHA-256 `872D2DCA8C21DDF9ACAC69C5F619E29A0E554B25B6537BFC1F448072916BB1A7`.
- `full_test115_x2_fast`: best recorded validation loss `0.002840859`; SHA-256 `8C87AC897EBFD7C166CB99F4A7B8922BFC4552BE79C242ABB39194C3DA21C3B8`.

Both use stride 2, 115 test cases, 60-epoch budget, 64 features, 16 blocks and window step 2. The `fast` profile changes batching/cache and disables shuffled windows. Because the standard run plateaued at a much poorer validation loss, the frozen rule selects the completed checkpoint with the lower pre-test validation loss:

`D:\MRI\baseline\ixi_i3net\runs\full_test115_x2_fast\checkpoints\i3net_epoch_best.pth`

No x2 test model output or metric existed when this choice was frozen.

## Frozen command

```powershell
$env:PYTHONPATH='D:\MRI\pre;D:\MRI\baseline;D:\MRI\design;D:\MRI'
& 'D:\conda\envs\MRI\python.exe' -B -m ixi_i3net.run_all `
  --profile full_test115_x2_fast `
  --eval-only-checkpoint 'D:\MRI\baseline\ixi_i3net\runs\full_test115_x2_fast\checkpoints\i3net_epoch_best.pth'
```

This command performs no training. It stages the frozen 115-case evaluation inputs, runs I3Net inference, runs the fixed linear/cubic comparators and writes evaluation metrics.

## Frozen consequence endpoint

- x4 error: existing definition-matched x4 examination MAE.
- x2 error: median missing-plane MAE from the frozen x2 output, using the same foreground mask convention.
- benefit: `x4_error - x2_error`; positive means densification reduces retrospective reconstruction error.
- score: unchanged `ANCHOR_CV_V1` computed only from acquired x4 anchors.
- budgets: 10%, 20%, 30%, 50%.
- comparisons: random expectation, oracle, adjacent-anchor MAE, Anchor-CV, and any already-frozen output score with a valid IXI case match.
- statistical unit: examination; 115 independent IXI examinations.

No endpoint, mask, budget, score or checkpoint may be changed after observing x2 test results.
