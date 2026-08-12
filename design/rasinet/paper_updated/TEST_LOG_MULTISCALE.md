# Multiscale Test Log

Run date: 2026-07-29

## Unit tests

Command:

```powershell
$env:PYTHONPATH="D:\MRI\pre;D:\MRI\design"
D:\conda\envs\MRI\python.exe -B -m unittest -v tests.test_rasinet_icassp_scores tests.test_rasinet_multiscale
```

Result: 26 tests passed. The tests cover generated support, target self-exclusion,
committee-size-one behavior, paired bootstrap identity reuse, common model
intersection, missing cases, OOF fold parsing, case-order invariance, oracle/random
risk-coverage behavior, and scoring/evaluation separation.

Independent command:

```powershell
$env:PYTHONPATH="D:\MRI\design"
D:\conda\python.exe -B -m pytest -q D:\MRI\tests\test_rasinet_multiscale.py
```

Result: 12 tests passed. The MRI environment does not currently include pytest,
so its full suite was run through `unittest`; the base environment supplied the
independent pytest run for the new module.

## Full experiment

Command:

```powershell
$env:PYTHONPATH="D:\MRI\pre;D:\MRI\design"
D:\conda\envs\MRI\python.exe -B -m rasinet.run_cross_scale_evaluation --config D:\MRI\design\rasinet\configs\multiscale_primary.yaml
```

Result: completed in 972.1 seconds, producing 966 per-case method rows, 18 fixed
primary profiles, and 2,000 paired bootstrap resamples.

## LaTeX validation

- `paper_icassp_regular_multiscale.pdf`: 5 pages; pages 1--4 technical, page 5 references.
- `paper_extended_multiscale.pdf`: 9 pages; pages 1--8 technical, page 9 references.
- Final logs contain no LaTeX error, undefined citation/reference, or overfull box.
- All fonts reported by `pdffonts` are embedded; no Type 3 fonts were found.
  Plot labels use embedded CID TrueType DejaVu fonts and manuscript text uses
  embedded Type 1 fonts.
