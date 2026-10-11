# ON-Harmony repeated-T2 source gate

Frozen before opening the Nature article or official dataset endpoint. Candidate: *A multi-site, multi-modal travelling-heads resource for brain MRI harmonisation*, DOI 10.1038/s41597-025-04822-2. The indexed abstract reports 20 participants, 165 scanning sessions, T2w in each session and approximately half the participants with five within-scanner repeats.

First obtain the public article HTML, preserve the exact response URL, byte count and SHA-256. Read the acquisition table, scanner/protocol specifics, T2w sequence dimensionality, within-scanner repeat structure and data availability/license text. Then inspect only the linked official metadata catalog, if public and bounded. Do not download image content in this stage.

For the project's native 2D slice-identity experiment, eligibility requires independently acquired 2D T2w, same subject and scanner/protocol, acquisition chronology, enough paired native slice centers and in-plane geometry, and usable research/publication rights. A 3D T2w acquisition, resampled release or cross-scanner-only repetition does not satisfy that contract. If the paper does not establish these facts, document unknowns; no pixel experiment and no GPU. Keep the running training process and locked IXI test untouched.
