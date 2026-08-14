# Build Instructions

From this directory, build the main paper with:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Build the supplement analogously with `supplement.tex` and `bibtex supplement`.

The scientific-content target is eight CVPR pages; additional pages may contain references only under the verified target-year template policy. Replace the placeholder paper ID and complete human authorship, ethics, disclosure, and compute-reporting fields before submission.
