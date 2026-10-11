# Targeted native 2D T2 retest source search

Frozen before the follow-up API requests. The previous three-query search began in 2015 and was noisy; this follow-up uses OpenAlex public Works metadata with no publication-date floor, three exact query strings, at most 50 default-relevance records each, and only a minimal selected field set. Queries:

1. `2D T2 weighted brain MRI scan rescan dataset`
2. `test retest T2 weighted fast spin echo brain MRI data`
3. `repeat acquisition T2 brain MRI DICOM open dataset`

Archive the full raw responses, exact URLs and SHA-256 hashes; deduplicate by work ID. Screen titles and indexed abstracts for a publicly traceable source with same-subject two independent acquisitions of structural T2w, preferably multislice 2D, file-level chronology/protocol/geometry and usable access terms. Do not promote titles or snippets to file eligibility; a promising record must pass official publication, archive, rights and nonpixel-header review before any pixel read. Report both plausible leads and exclusions. This is not a systematic review or novelty certificate. No GPU, ongoing training process or locked IXI test is involved.
