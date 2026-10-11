# Bounded OpenAlex check: shared measurement and paired MRI error

Frozen before retrieval on 2026-10-01. Purpose: supplement the earlier five arXiv queries with a cross-venue index search for a direct same-target measurement/context-switch audit. This is a collision screen, not a systematic review or proof of priority.

Endpoint `https://api.openalex.org/works`, relevance default, `per-page=25`, one first page per exact search string:

1. `magnetic resonance image reconstruction ensemble shared measurements disagreement error`
2. `MRI slice interpolation uncertainty correlated errors`
3. `medical image reconstruction measurement overlap ensemble uncertainty`
4. `scan rescan MRI reconstruction error correlation`

Archive each raw JSON response and a deduplicated index with DOI, publication year, primary location and reconstructable abstract. Exclude unrelated modality, segmentation-only work and generic survey titles from full-text selection, but retain them in raw responses. Escalate any work that actually fixes a target/reference, changes another estimator's observed MRI measurement/context set and measures paired error or disagreement against target truth. Read apparent direct collisions beyond the abstract before revising novelty language. Missing abstracts, index coverage, search ranking and the first-page cap prevent a global novelty conclusion.
