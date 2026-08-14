# Build and verification

From this directory:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex

pdflatex -interaction=nonstopmode -halt-on-error supplement.tex
pdflatex -interaction=nonstopmode -halt-on-error supplement.tex
```

Submission figures are regenerated from frozen CSV tables with:

```powershell
& D:\conda\envs\MRI\python.exe -B ..\scripts\plan6_make_submission_figures.py
```

Last verified 2026-08-13:

- `main.pdf`: 9 pages total = 8 content pages plus references.
- `supplement.pdf`: 5 pages.
- no undefined references/citations or overfull/underfull boxes.
- main and supplement logs have no undefined references/citations, overfull/underfull boxes, or float-only pages.
