# Bounded shared-context prior-art refresh

Frozen before the arXiv API retrieval on 2026-10-01. Purpose: look for a direct prior experiment in MRI reconstruction or through-plane interpolation that changes two estimators' observed inputs on the same target and quantifies correlated error or disagreement reliability. This is a focused novelty collision check, not a systematic review or proof of priority.

Use the public arXiv Atom API, relevance order, first 30 hits per exact query:

1. `all:"MRI reconstruction" AND all:disagreement`
2. `all:MRI AND all:"correlated errors" AND all:ensemble`
3. `all:"MRI reconstruction" AND all:uncertainty AND all:ensemble`
4. `all:"slice interpolation" AND all:uncertainty`
5. `all:"complementary sampling" AND all:MRI`

Archive raw Atom responses and a parsed title/abstract/ID/date index. Deduplicate by arXiv base ID. Screen all unique titles and abstracts for (a) MRI reconstruction/interpolation rather than segmentation or unrelated imaging; and (b) output disagreement, common error, input/mask/measurement overlap or complementary sampling. Read the full text of apparent direct collisions before deciding novelty. Do not treat absence in these bounded results as proof that no prior work exists. No GPU, patient images or existing training processes are involved.
