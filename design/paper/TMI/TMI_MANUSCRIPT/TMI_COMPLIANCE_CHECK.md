# TMI compliance and reviewer audit

Audit date: 2026-08-13. Target: TMI Regular Paper initial submission.

## Mechanical compliance

| Item | Result | Evidence |
|---|---|---|
| IEEE-compatible journal class | PASS | Local fixed `IEEEtran.cls` v1.8b; CTAN archive retained in `vendor/` |
| Page limit incl. references | PASS | Final LaTeX log: 6 pages, maximum 10 |
| Font size | PASS | IEEEtran log: “This is a 10 point document” |
| Two-column letter layout | PASS | 612 x 792 pt; visual audit pages 1--5 |
| Abstract <250 words | PASS | 220 words by regex token audit |
| Index terms | PASS | Seven IEEE keywords present |
| Embedded fonts | PASS | `pdffonts`: every listed font `emb=yes`, `sub=yes` |
| Citations / references | PASS | BibTeX plus two pdflatex passes; no undefined reference/citation in final log |
| Overfull boxes | PASS | None in final log; underfull bibliography wrapping is cosmetic |
| Figure placement/readability | PASS | Five programmatic figures visually inspected at 110 dpi; labels readable |
| File size | PASS | 323,766 bytes, below 40 MB |
| Figures/tables in main text | PASS | Five figures and two tables embedded |
| Author biographies | PASS | None |
| Supplement | NOT USED | Current TMI policy does not allow a supplement to evade page/content rules |

## Enrichment pass (2026-08-13)

The manuscript was expanded without changing the frozen evidence ledger. Added material clarifies the common-mode and anti-aligned error limits, distinguishes diversity from observability and calibration, explains hierarchical patient resampling, and strengthens the MRI-specific interpretation of physical anchors. The revised document compiles at 6 pages/10 pt with no overfull boxes or undefined citations/references.

## Evidence audit

- All main numerical claims trace to immutable Plan-2--4 outputs or the explicitly superseding patient-cluster correction.
- IXI (115 cases) appears only in the frozen auxiliary difficulty analysis; new CVPR IXI overlap results are excluded.
- Dense MRI targets are used only for retrospective phase-grid synthesis and evaluation, not in the reliability score.
- NingXia is correctly described as knee T2, 22 series from eight patient groups.
- Negative findings remain visible: common-mode/stable-wrong boundary, no fastMRI natural stable-wrong event, failed universal curvature transfer, and no corrected NingXia PC-vs-TTA significance.

## Simulated reviewer audit

### A — Imaging significance: PASS with scope caveat

The intervention is tied to acquired through-plane anchors, NIfTI physical-plane matching, and densification. It is not generic uncertainty pasted onto MRI. Prospective acquisition remains absent and is explicitly limited.

### B — Novelty: PASS for TMI positioning

The paper is positioned around measurement overlap and error observability, distinct from proposing another calibrated uncertainty score. The closest uncertainty and ensemble works do not test the same target-preserving overlap intervention according to the bounded literature audit.

### C — Statistics: PASS after supersession

fastMRI resampling uses 24 cases. NingXia inference now uses eight patient prefixes, retaining subordinate series/planes/models. The original 22-series inference remains immutable but is superseded. Plane-level statistics are identified as descriptive ranking with cluster intervals.

### D — Medical rigor: CONDITIONAL

Anatomy and public-data provenance were corrected. Exact NingXia IRB/consent information is absent from the repository and must come from authors.

### E — Mechanism: PASS with stated confound

Same target/case/model/plane/mask are paired. The maximal-overlap reversal control changes order as well as overlap; the paper does not claim pure causal identification and reserves cleaner controls for the exploratory branch.

### F — Claims: PASS

No calibrated uncertainty, correctness certification, clinical safety, prospective acquisition, universal superiority, or output-attribution claim remains.

## Irreducible pre-submission blockers

The compiled research manuscript is complete, but it is **NOT SUBMISSION-READY FOR UPLOAD** until humans supply:

1. author names, affiliations, corresponding author, funding, and ORCIDs;
2. NingXia approving/exempting institution, approval/decision identifier where applicable, consent/waiver, and data-use wording;
3. exact public-release consent/ethics wording adopted by the authors for fastMRI and IXI;
4. anonymized code/data URL and internal-data sharing restrictions;
5. confirmation of any IEEE-required AI-content disclosure.

These values are intentionally not fabricated.

## Final enriched visual audit

All six pages of the 2026-08-13 enriched build were rasterized and inspected. The new reliability-design, diversity/observability/calibration, hierarchical-resampling, and physical-anchor interpretation paragraphs introduce no clipped text, broken columns, overfull boxes, or new numerical evidence. Page 6 contains references only. Plan5+ CVPR experiments remain excluded.
