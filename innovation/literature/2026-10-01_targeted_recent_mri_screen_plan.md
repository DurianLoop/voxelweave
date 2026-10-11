# Targeted recent MRI prior-art screen

Frozen before retrieval on 2026-10-01. Search OpenAlex for 2024-2026 work using four title/abstract queries, at most 50 most recent records per query:

1. `MRI reconstruction uncertainty ensemble pathology`
2. `MRI reconstruction shared measurements correlated errors`
3. `MRI slice interpolation uncertainty context`
4. `MRI reconstruction lesion segmentation uncertainty`

Archive each raw API response, URL, SHA-256 and a deduplicated title/abstract index. Screen titles and available abstracts for a same-target intervention that changes one estimator's observation/context set while keeping the other estimator and target fixed, or for task-level lesion consequences under MRI reconstruction. Escalate plausible collisions to lawful full text; abstract-only records remain unresolved. This is a bounded discovery screen, not a systematic search or a priority certificate. No GPU or patient data is used.
