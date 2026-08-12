# ACSI-Net vs I3Net Case Gap Diagnosis

Positive gaps mean I3Net has larger error than ACSI-Net, so ACSI-Net is better. Negative gaps mean I3Net is better.

## Worst ACSI-Net Cases vs I3Net

| Case | Mean I3-ACSI | ZGE | ZLE | EdgeZ | NCC-z-MAE |
| --- | --- | --- | --- | --- | --- |
| IXI417-Guys-0939-T2.nii.gz | -0.007729 | -0.004802 | -0.008206 | -0.002144 | -0.015764 |
| IXI585-Guys-1130-T2.nii.gz | -0.007644 | -0.004950 | -0.008262 | -0.002675 | -0.014690 |
| IXI405-Guys-0948-T2.nii.gz | -0.006994 | -0.004783 | -0.007769 | -0.003093 | -0.012330 |
| IXI210-Guys-0856-T2.nii.gz | -0.006361 | -0.004517 | -0.007371 | -0.002730 | -0.010825 |
| IXI560-Guys-1070-T2.nii.gz | -0.006235 | -0.003914 | -0.006242 | -0.002636 | -0.012148 |
| IXI134-Guys-0780-T2.nii.gz | -0.005619 | -0.003345 | -0.005620 | -0.001285 | -0.012228 |
| IXI129-Guys-0775-T2.nii.gz | -0.005295 | -0.003281 | -0.005206 | -0.002179 | -0.010515 |
| IXI591-Guys-1084-T2.nii.gz | -0.005183 | -0.003630 | -0.005787 | -0.002036 | -0.009276 |
| IXI288-Guys-0879-T2.nii.gz | -0.005113 | -0.003692 | -0.005829 | -0.002434 | -0.008496 |
| IXI393-Guys-0941-T2.nii.gz | -0.004755 | -0.002939 | -0.004584 | -0.001930 | -0.009566 |

## Best ACSI-Net Cases vs I3Net

| Case | Mean I3-ACSI | ZGE | ZLE | EdgeZ | NCC-z-MAE |
| --- | --- | --- | --- | --- | --- |
| IXI014-HH-1236-T2.nii.gz | 0.002311 | -0.000089 | 0.000090 | 0.000134 | 0.009111 |
| IXI605-HH-2598-T2.nii.gz | 0.000413 | -0.000061 | 0.000211 | -0.000025 | 0.001524 |
| IXI131-HH-1527-T2.nii.gz | 0.000392 | -0.000370 | -0.000081 | -0.000336 | 0.002356 |
| IXI353-HH-1996-T2.nii.gz | 0.000278 | 0.000425 | 0.001200 | 0.000299 | -0.000812 |
| IXI260-HH-1805-T2.nii.gz | 0.000174 | -0.000132 | 0.000207 | -0.000047 | 0.000667 |
| IXI211-HH-1568-T2.nii.gz | 0.000046 | -0.000481 | -0.000223 | -0.000250 | 0.001140 |
| IXI537-HH-2378-T2.nii.gz | -0.000262 | 0.000151 | 0.000533 | 0.000405 | -0.002138 |
| IXI606-HH-2601-T2.nii.gz | -0.000451 | 0.000079 | 0.000500 | 0.000083 | -0.002465 |
| IXI261-HH-1704-T2.nii.gz | -0.000456 | 0.000024 | 0.000512 | 0.000063 | -0.002424 |
| IXI601-HH-2700-T2.nii.gz | -0.000576 | -0.000646 | -0.000428 | -0.000365 | -0.000862 |

## Suggested Visual QC

Generate sagittal/coronal panels for the worst ACSI-Net cases first. If these cases show systematic discontinuity, ACSI-v2 needs longer z-context rather than only loss-weight tuning.
