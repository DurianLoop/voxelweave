# Archived two-source full-support model versus raw-linear check

The [post-result rule](TWO_SOURCE_EQUAL_NEIGHBOR_PERFORMANCE_CHECK_PLAN_2026-10-01.md) joined the exact existing IXI-weight HAT/SwinIR and linear-partner target CSVs; it decoded no images, loaded no models and used no GPU. For every target, patient, residue, acquired-foreground support size, z spacing and fixed HAT MAE matched. The [script](experiments/two_source_equal_neighbor_performance_check.py), [patient table](experiments/two_source_equal_neighbor_performance_check/per_patient.csv) and [summary](experiments/two_source_equal_neighbor_performance_check/summary.json) retain the read-only results.

| Whole acquired foreground | Completed patients / targets | Raw linear0 MSE | HAT0 MSE; HAT minus linear | SwinIR0 MSE; SwinIR minus linear |
|---|---:|---:|---:|---:|
| MSValid RRMS | 84 / 479 | 59,365.59 | 50,664.20; **-8,701.39** (84/84 patients lower) | 50,744.86; **-8,620.73** (84/84 lower) |
| TCIA ReMIND | 62 / 248 | 59,280.63 | 50,129.21; **-9,151.42** (62/62 lower) | 50,518.34; **-8,762.29** (62/62 lower) |

All means use target-within-residue, residue-within-patient and patient-equal averaging in each source's own raw intensity units. An independent PowerShell aggregation reproduced MSValid HAT-minus-linear -8,701.38777531432 and ReMIND SwinIR-minus-linear -8,762.29196186853. Do not pool or subtract the absolute MSE values across sources. These are **whole-support** endpoints, not tumor ROIs; neither source provides a directly matched label task here. Their result-after linear partner experiment and this later cross-read share the original models and patients, so this is a context check rather than an independent validation.

The later [MSD full-support check](MSD_FULL_SUPPORT_EQUAL_NEIGHBOR_POSTRESULT_RESULT_2026-10-01.md) is necessary before claiming that the MSD tumor finding represents a dataset-wide reversal. It finds a different overall pattern from the MSD tumor ROI. No causal conclusion about disease, acquisition or domain shift follows from this cross-source table.
