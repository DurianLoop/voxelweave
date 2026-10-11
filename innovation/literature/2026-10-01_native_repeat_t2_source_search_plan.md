# Bounded search for independently repeated T2 MRI sources

Frozen before the full API retrieval on 2026-10-01. Search the public OpenAlex Works API with exactly three queries, each capped at 25 default-relevance records published from 2015-01-01 onward:

1. `test retest T2 weighted MRI dataset brain`
2. `scan rescan T2 MRI open dataset`
3. `repeated acquisition T2 weighted brain MRI public data`

Archive exact URLs, raw JSON responses and SHA-256 hashes, then deduplicate by OpenAlex work ID. Screen titles and available indexed abstracts only for datasets that might expose two **independently acquired** T2w measurements for the same patient with usable nonpixel series headers. A candidate must have a lawful accessible source, acquisition chronology, matching native protocol/geometry and enough patients before any pixel experiment. Exclude repeat reconstruction of one measurement, longitudinal scans too distant for matched anatomy, other MRI contrasts, simulated repeats and source pages without file-level access. This bounded metadata search cannot establish data rights, geometric eligibility or a novel claim; exact candidate datasets require official-source checks before use. No patient data, GPU or running training process may be touched.
