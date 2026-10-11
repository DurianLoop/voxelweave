# Frozen citation-neighbour novelty screen for MIRA

**Purpose:** check whether papers citing Hu, Pezzotti and Welling's 2021 MRI error-prediction work, or recent targeted OpenAlex results, already perform MIRA's fixed-target shared/disjoint published-slice-context audit. This is a bounded collision search, not a systematic review or proof of priority. The query plan is fixed before retrieving the full response sets. The OpenAlex DOI lookup for Hu 2021 returned work ID `W3204136415`, title *Learning to Predict Error for MRI Reconstruction* and 11 citing works at lookup time.

Use the public OpenAlex works API, archive exact raw responses and SHA-256, and request at most 50 results per query:

1. `filter=cites:W3204136415` (all currently indexed citing works).
2. `search=MRI reconstruction error correlation ensemble`, `filter=from_publication_date:2022-01-01,to_publication_date:2026-10-01`.
3. `search=MRI through-plane interpolation uncertainty`, same date filter.
4. `search=magnetic resonance reconstruction shared measurement disagreement`, same date filter.

For each retrieved work retain ID, DOI, year, title, source, cited-by count, open full-text URL and reconstructed abstract when available. Deduplicate by OpenAlex work ID, then title/abstract screen every unique result for direct collision. Escalate to full text only if the paper actually fixes a target/reference, varies another estimator's observed physical or published image context, and measures paired error or output disagreement against target truth. Distinguish k-space masks, posterior samples, segmentation, and fully supervised error prediction from through-plane released-slice context. Missing abstract, first-page truncation, imperfect indexing and citation gaps prohibit a global novelty conclusion. No patient images, GPU or training process are involved.
