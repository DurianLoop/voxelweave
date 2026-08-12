# Unresolved Multiscale Items

## Must resolve before submission

1. **NingXia governance statement.** The manuscript calls this an internal,
   de-identified, eight-fold OOF cohort. The final submission still needs the
   correct ethics/consent wording and approval identifier supplied by the data
   owner. No placeholder was inserted into the anonymous paper.
2. **Author and conference metadata.** Restore author names, affiliations,
   funding, and the final ICASSP 2027 template metadata only after anonymity and
   conference instructions are confirmed.

## Important remaining evidence gaps

1. No reader study or downstream diagnostic task is available. This limits the
   claim to MAE-based review ranking and does not invalidate the reported result.
2. Online full-committee latency and peak GPU memory were not measured on one
   matched device. The paper reports the measured stored-output CPU audit cost
   and explicitly separates it from online neural inference.
3. Evidence remains T2 brain MRI. Adding a contrast or anatomy would broaden
   scope but is not required for the current bounded claim.
4. TTA is available only for fastMRI-brain x4 SwinIR and is reported as a local,
   paired comparison; it must not be averaged across unavailable profiles.

## Reproducible outputs

No multiscale result is pending execution. Re-run the full analysis with:

```powershell
$env:PYTHONPATH="D:\MRI\pre;D:\MRI\design"
D:\conda\envs\MRI\python.exe -B -m rasinet.run_cross_scale_evaluation --config D:\MRI\design\rasinet\configs\multiscale_primary.yaml
```

Expected output root: `D:\MRI\design\rasinet\outputs\multiscale`.
