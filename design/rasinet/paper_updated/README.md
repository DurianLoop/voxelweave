# ICASSP Regular Paper - Visual Relayout

This package contains the revised Overleaf/LaTeX source and the checked five-page PDF.

## Build

```bash
./build.sh
```

or run manually:

```bash
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

## Output

- `paper_icassp_regular_visual_relayout.pdf`
- Pages 1-4: technical content
- Page 5: references only

## Layout changes

- Method workflow remains beside the method text on page 1.
- Cohort/protocol and complete ten-profile results are embedded in the experiment narrative.
- Page 3 interleaves two result tables, the shared-error plot, and qualitative MRI examples.
- Page 4 combines risk-coverage curves, TTA/cost comparison, discussion, and limitations.
- References fill the fifth page without spilling to a sixth page.
