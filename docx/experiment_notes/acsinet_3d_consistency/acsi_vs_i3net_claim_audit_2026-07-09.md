# ACSI-Net vs I3Net Claim Audit

## Claim Gate

The strong ACSI-Net claim requires two wins against I3Net:

1. ACSI-Net must be lighter than I3Net.
2. ACSI-Net must beat I3Net on anatomy-consistency metrics, not only linear/cubic.

## Lightweight Evidence

| Method | Params M | FLOPs / generated slice G |
| --- | --- | --- |
| ACSI-Net | 0.344 | 14.684 |
| I3Net | 23.205 | 100.776 |
| I3/ACSI ratio | 67.409 | 6.863 |

## Anatomy Consistency Evidence

| Method | Cases | ZGE | ZLE | EdgeZ | NCC-z-MAE |
| --- | --- | --- | --- | --- | --- |
| acsinet | 115 | 0.0113 | 0.0178 | 0.0099 | 0.0256 |
| i3net | 115 | 0.0097 | 0.0155 | 0.0090 | 0.0197 |

## ACSI-Net Per-Case Wins vs I3Net

| Metric | ACSI wins | Win rate | Mean I3-ACSI |
| --- | --- | --- | --- |
| zge | 5/115 | 0.043 | -0.001605 |
| zle | 9/115 | 0.078 | -0.002244 |
| edge_z_error | 7/115 | 0.061 | -0.000974 |
| interslice_ncc_mae | 5/115 | 0.043 | -0.005893 |

## Interpretation

ACSI-Net does not yet pass the strong-claim gate against I3Net on this audit. It can still be discussed as a lightweight competitive model, but the anatomy-consistency claim must be weakened unless visual QC or refined metrics show a clearer advantage.

The next step should be diagnosis: inspect the cases where I3Net wins, then decide whether to improve the loss/design or downgrade ACSI-Net to a supporting analysis direction.
