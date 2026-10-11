# Targeted 2026 arXiv refresh: frozen scope

Before retrieval, search arXiv API once for each of three exact queries, latest submission first, at most 100 entries/query:

1. `all:"slice interpolation" AND all:MRI`
2. `all:"through-plane" AND all:uncertainty`
3. `all:"MRI reconstruction" AND all:disagreement`

Archive raw Atom responses, URL, SHA-256, hit count and parsed titles/abstracts. Screen all returned titles; read abstracts of plausible method/measurement neighbors. A 2026 article becomes a full-text priority when its abstract tests error visibility or uncertainty under a change of physical observations, or reconstructs missing through-plane planes with an explicitly varied acquisition context. Otherwise label title/abstract only. Do not infer a global novelty claim from absent hits, query semantics or ranking. No GPU, patient images or running training process are involved.
