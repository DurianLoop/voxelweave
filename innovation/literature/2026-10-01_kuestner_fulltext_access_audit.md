# Kuestner 2024 full-text access audit

For Kuestner et al., *Predictive uncertainty in deep learning-based MR image reconstruction using deep ensembles: Evaluation on the fastMRI data set*, DOI `10.1002/mrm.30030`, the prior [citation-neighbour screen](2026-10-01_mira_citation_neighbour_result.md) had only formal metadata and an indexed abstract. This follow-up checked current public routes on 2026-10-01; it did **not** obtain the article body.

| Route | Observed result | Limit |
|---|---|---|
| OpenAlex work `W4391320131` and Semantic Scholar DOI record | Both index Wiley `https://onlinelibrary.wiley.com/doi/pdfdirect/10.1002/mrm.30030` as an open PDF. Semantic Scholar labels it hybrid/CC BY. Crossref lists a Wiley `/doi/pdf/` version-of-record link. | A metadata OA label is not a successfully retrieved full text. |
| Wiley `/doi/full/` and `/doi/epdf/` endpoints | Direct HTTP requests returned 403 in this environment; prior `/doi/pdfdirect/` attempt was also 403. | No methods, tables or mask/context-switch protocol could be checked. |
| Europe PMC DOI lookup | PubMed ID `38282254`, `isOpenAccess=N`, `hasPDF=N`, no PMCID/full-text URL in the returned record. | Europe PMC does not supply an alternate text here. |
| TUM mediaTUM item `1752940` | HTML metadata page includes the DOI but exposes no PDF link in this read-only check; a guessed `/doc/1752940/1752940.pdf` address returned HTML, not a PDF. | Repository item is not evidence that the article full text was read. |
| arXiv title query | No matching author preprint identified among returned results. | A bounded arXiv query does not prove no preprint exists elsewhere. |
| OpenAlex `content.openalex.org/works/W4391320131.grobid-xml` follow-up | OpenAlex metadata indexed a content XML URL, but a direct read-only GET on 2026-10-01 returned HTTP 401. The configured proxy refused connections; direct public work metadata remained reachable. | An indexed content URL is not a readable article body here. No credentials or alternate access were attempted. |

**Decision:** keep Kuestner as an **abstract-level** comparator. Its formal abstract already rules out broad novelty language about deep ensembles across architectures, sampling shifts and error correlation. Whether it contains an equivalent same-target released-slice context intervention remains unresolved. A later institutional/library or author-provided lawful copy would permit a proper methods-level collision audit; no protocol claim is made from inaccessible pages.
