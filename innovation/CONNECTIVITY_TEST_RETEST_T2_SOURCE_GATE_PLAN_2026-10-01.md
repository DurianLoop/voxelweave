# Connectivity test-retest dataset T2 source gate

Frozen before the article request. Candidate: *A connectivity-based test-retest dataset of multi-modal magnetic resonance imaging in young healthy adults*, DOI 10.1038/sdata.2015.56. Indexed abstract: 57 healthy adults, two MRI sessions approximately six weeks apart, each with S-MRI, D-MRI and resting-state fMRI.

Fetch the public Nature HTML with a bounded 2 MB response, archive URL/hash and inspect the acquisition table and data-availability section. The immediate gate is whether S-MRI includes a separately acquired **T2-weighted 2D** sequence in both sessions, rather than T1-only or 3D data. If not, stop without image or file-level requests. If yes, proceed later through the established license, patient/session pairing and nonpixel geometry gates. No GPU or locked IXI test.
