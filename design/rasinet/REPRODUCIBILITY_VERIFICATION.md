# Reproducibility Verification

## Verified

- 11/11 unit and integration tests passed with the MRI Python environment.
- Both papers compile without LaTeX errors, undefined citations/references, or overfull boxes.
- Regular PDF: 5 letter-size pages, pages 1--4 technical and page 5 references only.
- Extended PDF: 9 letter-size pages, pages 1--8 technical and page 9 references only.
- `pdffonts` reports embedded Type 1 or CID TrueType fonts; no Type 3 fonts.
- 528 first-pass and 528 amended decisions have `selection_used_outer_labels=False`.
- Every target is excluded from its own selected committee.
- Every final factor--target--method profile has all 22 outer cases.
- Every paired bootstrap group contains exactly 2,000 aligned replicates.
- All 1,518 physical records have matched generated planes.
- Main table and macros are generated from CSV, with claim provenance in `nested_claim_traceability.csv`.

## Reproduction

From precomputed features:

```powershell
cd D:\MRI
.\design\rasinet\reproduce_nested.ps1 -Mode from-precomputed
```

End to end from NIfTI predictions:

```powershell
cd D:\MRI
.\design\rasinet\reproduce_nested.ps1 -Mode recompute-features
```
