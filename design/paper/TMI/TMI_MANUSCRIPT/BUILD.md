# Build

From this directory, using MiKTeX with automatic missing-package installation enabled:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

The repository-local `IEEEtran.cls` is the fixed class used by the build. Final enriched audited output: 6 pages, 10 pt, letter, 323,766 bytes.
