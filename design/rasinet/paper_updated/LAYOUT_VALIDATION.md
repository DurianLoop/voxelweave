# Layout validation

## Page structure

- Page 1: Abstract, Introduction, Method, framework diagram.
- Page 2: Remaining Method, cohort/protocol setup, frozen evaluation protocol.
- Page 3: Main ten-profile table, ablation and sensitivity tables, shared-error plot, qualitative MRI examples.
- Page 4: Risk-coverage curves, TTA/cost table, Discussion and Conclusion.
- Page 5: References only, two-column layout filled close to the bottom margin.

## Checks performed

- Rendered all five pages at 180 dpi and visually inspected each page.
- No clipped labels, overlapping text, cropped tables, or unreadable micro-panels observed.
- `pdfinfo`: 5 pages.
- `pdffonts`: all fonts embedded; no Type 3 fonts.
- LaTeX log: no undefined references/citations and no overfull boxes.
- PDF preflight: openable, unencrypted, text-based PDF.
