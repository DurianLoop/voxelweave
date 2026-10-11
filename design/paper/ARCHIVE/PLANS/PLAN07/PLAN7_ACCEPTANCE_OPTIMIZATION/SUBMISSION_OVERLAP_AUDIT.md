# TMI–CVPR submission overlap audit

Audit date: 2026-08-14. Candidates: the E02-integrated `TMI_MANUSCRIPT_SUBMISSION_FINAL/main.tex` and `CVPR_UPGRADE/PAPER_FINAL/main.tex`. This is an internal scientific/textual audit, not CrossCheck or legal advice.

## 1. Textual overlap

Paragraph parsing excluded figures, tables and displayed equations. Pure-Python unigram/bigram TF-IDF cosine matched each of 63 TMI paragraphs to its closest among 47 CVPR paragraphs after the Plan7 findings rewrite.

- 2/63 TMI paragraphs exceeded cosine 0.30.
- 0/63 exceeded 0.45.
- Therefore 0/4,015 audited TMI words fall in a match above the prespecified 0.45 diagnostic threshold (0%).
- The two highest similarities are 0.326 and 0.318 and arise in shared theory/method descriptions; their sequence ratios are 0.088 and 0.079. There is no evidence of widespread verbatim duplication from this diagnostic.
- Evidence: `outputs/p7_submission_paragraph_overlap.csv` and `p7_submission_overlap.json`.

This does **not** prove policy-safe overlap. TMI's official checklist states less than 20% CrossCheck overlap for a journal extension of a conference paper, but only an actual publisher report can establish that threshold.

## 2. Paragraph/section classification

| Content block | Classification | Action |
|---|---|---|
| MRI interpolation problem/background | Shared background | Keep independently worded and cite same task precedents. |
| Elementary error-difference decomposition | Shared historical evidence | Minimize in CVPR; explicitly non-novel in both. |
| Three cohort descriptions | Shared background/data | Disclose reuse; avoid calling cohorts independent across papers. |
| Physical zero-vs-maximal overlap intervention | TMI only / shared historical evidence for CVPR | Full results remain TMI; CVPR may mention motivation but must not count as its independent contribution. |
| Seven endpoints, x2/x4/x6, geometry/intensity, stable-wrong | TMI only | Exclude from CVPR main contribution. |
| TMI false-retention QA and operating regimes | TMI only | Do not copy into CVPR. |
| Analytical coefficient influence ladder | CVPR only | Retain only in CVPR. |
| Neural finite-difference shared influence | CVPR only | Central CVPR evidence if P7 stability passes. |
| Fixed-count influence analysis and mechanism arrows | CVPR only | Retain with counterexamples. |
| Anchor-CV/adjacent/PC audit | CVPR only but method is historical | Demote from contribution; no unique/superiority claim. |
| P7 failed selector, jackknife and residualization | CVPR only | Use as failure boundary/supplement, not TMI. |
| Retrospective densification benefit | Scientifically shared consequence risk | TMI may report existing QA consequence; CVPR should not count it as a separate central contribution after method gates fail. |
| Ethics, data sources, statistical hierarchy | Shared required metadata | Independent wording; disclose reuse. |

## 3. Figure classification

| TMI figure | CVPR relation | Classification / decision |
|---|---|---|
| TMI Fig. 1 shared evidence → aligned error → hidden disagreement | CVPR Plan7 Fig. 1 shows count-matched contexts, finite-difference influence, evidence boundary and failed method gates | **Separated after redesign.** Visual audit confirms different layout, variables and reviewer message. |
| TMI design phase grids | CVPR clean overlap motivation | TMI only as full intervention figure; CVPR uses a compact context/influence schematic if retained. |
| TMI overlap ranking | Historical motivating result in CVPR | TMI only; CVPR should not display same outcome figure. |
| TMI endpoint/factor/intensity/risk panels | No direct CVPR counterpart | TMI only. |
| CVPR neural influence forest/mechanism chain | No TMI counterpart | CVPR only. |
| CVPR Anchor-CV/risk/benefit panels | TMI contains related risk/densification tables | **Moderate scientific overlap.** These are demoted from the CVPR main contribution and retained mainly as capability falsification/context. |

## 4. Experiment and claim overlap

There are 12 major TMI experiment families and roughly 10 major CVPR families. Four scientific foundations are shared: cohort/model outputs, same-target overlap motivation, error-energy definitions, and retrospective QA framing. The decisive result families are otherwise separable: TMI owns systematic physical-intervention characterization; CVPR owns nonlinear influence measurement and its falsification boundaries. However, because P7-CV-E01/E03/E04 failed, the CVPR candidate lacks an independent capability and leans more heavily on the same physical-dependence story. Scientific overlap is therefore estimated qualitatively as **moderate-to-high**, despite low text similarity.

## 5. Submission policy risk

- Simultaneous review could be judged duplicate/concurrent submission depending on final manuscripts and disclosure. Automated analysis cannot authorize it.
- The CVPR 2026 author policy restricts concurrent substantially similar submissions; TMI requires disclosure and limits overlap when extending conference work.
- TMI and CVPR central sentences are distinct only if CVPR is confined to continuous neural influence and rigorous negative findings.
- The current evidence does not support two simultaneous “method/capability” submissions.

## 6. Verdict

**MERGE_OR_SEQUENCE_REQUIRED.** Recommended sequence:

1. Finish TMI human metadata and submit/resolve the TMI imaging-method paper first.
2. Do not concurrently submit the current CVPR candidate.
3. If P7-CV-E02 passes, preserve the CVPR work as a later, substantially re-scoped mechanism/findings submission with explicit disclosure and reduced shared QA evidence.
4. If E02 fails, merge the neural influence audit and negative method portfolio into the TMI supplement/future revision rather than forcing a separate CVPR paper.

Only the authors and venue editors can make the final policy decision. No automatic submission is permitted.
