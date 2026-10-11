# Current TMI Requirements

Verified: 2026-08-13. Target article: **Regular Paper, initial submission**.

## Authoritative sources

- TMI Instructions to Authors, revision 10.2 (2025-10-09): https://ieeetmi.org/authors-instructions/
- TMI Submission Checklist: https://ieeetmi.org/submission-checklist/
- IEEE journal article templates and Template Selector: https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/authoring-tools-and-templates/tools-for-ieee-authors/ieee-article-templates/
- IEEE article structure: https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-the-text-of-your-article/structure-your-article/
- IEEE submission, human-subject, and AI-content policies: https://journals.ieeeauthorcenter.ieee.org/become-an-ieee-journal-author/publishing-ethics/guidelines-and-policies/submission-and-peer-review-policies/
- IEEE supplementary-material guidance: https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/prepare-supplementary-materials/

## Verified requirements

| Item | Current requirement | Implementation/evidence |
|---|---|---|
| Article type | Regular Paper | `main.tex` uses journal format and labels the package accordingly |
| Initial length | At most 10 pages **including references** | final PDF page audit required |
| Font/layout | At least 10-point; double-column; single-spaced; figures/tables embedded | official-compatible IEEE transactions class; no margin/font overrides |
| Abstract | One paragraph, at most 250 words, self-contained, no citations/equations | automated word-count audit |
| Index terms | Required; approximately 3--5 standardized terms/phrases | `IEEEkeywords` in `main.tex` |
| References | IEEE author-name style, complete metadata; all authors when six or fewer, otherwise first author *et al.* | BibTeX records verified against primary/official records |
| Figures/tables | Embedded in main text for initial submission; do not upload high-resolution figures separately | all manuscript figures included in PDF |
| Supplement | Since 2022, no text/figure/table extension of manuscript. Allowed types: graphical abstract, video, media, dataset, code, and conference predecessor | `supplement.tex` is an internal reproducibility source and marked **NOT FOR TMI SUPPORTING-DOCUMENT UPLOAD** |
| Biographies | Do not include author biographies | omitted |
| PDF | One complete PDF for initial submission, under 40 MB | size audit required |
| Submission system | IEEE Author Portal; submitting author requires ORCID | human submission step; `NOT RUN` |
| Anonymity | TMI journal instructions require author/affiliation information rather than anonymous review formatting | placeholders retained until authors supply exact data |
| Human subjects | Name the responsible review board/committee and approval or explain why review was not conducted; report consent or explain why not | fastMRI public/deidentified status cited; NingXia statement remains `[ETHICS INFORMATION REQUIRED FROM AUTHORS]` |
| Data/code | Open-source code is encouraged; supporting documents may include dataset/code | reproducibility paths and prospective release statement included, without promising a URL |
| AI-generated content | IEEE policy requires disclosure of AI-generated article content, identifying the system and affected sections/level; editing-only use is generally outside the mandatory scope but disclosure is recommended | explicit author-review placeholder in acknowledgments/compliance check |
| Prior/dual publication | Work must not be under consideration elsewhere; conference extension must be disclosed and substantially extended | governed by `SUBMISSION_STRATEGY.md`; no submission performed |

## Differences from the working assumptions

The Plan-5 working assumptions (10 pages including references, 10-point minimum, abstract below 250 words, IEEE index terms) agree with the current official requirements. The important additional current constraint is that ordinary manuscript-extension supplements are not permitted.

## Human actions still required before actual submission

- Supply author names, affiliations, institutional email addresses, corresponding author, ORCID, funding, and conflicts.
- Supply the exact NingXia ethics committee, decision/approval identifier if applicable, and consent/waiver basis.
- Review and approve the IEEE AI-use disclosure wording.
- Confirm prior-review/rejection history and whether a cover letter is permitted/required.
- Validate the final source with IEEE LaTeX Analyzer/PDF Checker and upload through IEEE Author Portal.

