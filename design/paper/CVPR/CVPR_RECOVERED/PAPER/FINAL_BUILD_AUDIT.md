# Final CVPR Build Audit

Date: 2026-08-14

## Build result

- Main manuscript: `main.pdf`, 9 total pages = 8 scientific pages + 1 references page.
- Supplement: `supplement.pdf`, 4 pages.
- Main and supplement compile successfully with MiKTeX `pdflatex`; the main bibliography is resolved with BibTeX.
- Final logs contain no LaTeX warning, overfull/underfull box, undefined-reference, or undefined-citation diagnostics.
- PDF text scan found no `TODO`, `TBD`, `PLACEHOLDER`, or `undefined` marker.

## Visual audit

- Main pages 1–9 and supplement pages 1–4 were rendered to PNG for inspection.
- The four central figures are legible at two-column width and use consistent dataset/model encoding.
- Tables remain inside margins; no clipped captions, orphaned headings, or blank pages were observed.
- Page 8 now contains the interpretation boundary, operational reading, falsifiable predictions, deployment limits, negative-result validation protocol, and conclusion. Page 9 contains references only.

## Scientific boundary audit

- IXI is primary replication evidence with 115 examinations; fastMRI is the other primary cohort.
- NingXia is reported as an eight-patient heterogeneity boundary, including its null/mixed fixed-count result.
- Raw overlap count is not claimed to obey a universal monotone law.
- Neural influence is a local target–context–input response diagnostic, not a plane-invariant global model coefficient.
- The local mechanism chain is separated from the weaker global context-ranking arrow.
- Anchor-CV is described as acquired-only and inexpensive, not uniquely informative, calibrated, pixel-local, or universally superior.
- No prospective scanner-control, diagnostic-safety, causal-mediation, or outside-MRI empirical claim is made.
- Failed Plan-7 selectors/corrections remain documented and are not promoted as contributions.

## Required submission-time human checks

- Replace anonymous paper ID placeholders when issued by the venue.
- Confirm author list, affiliations, acknowledgements, funding, ethics statements, and dataset-license wording.
- Make and document a compliant submission-sequencing/disclosure decision relative to the related TMI manuscript.
- Re-run the build with the exact official target-year CVPR author kit if the venue releases a template revision.
