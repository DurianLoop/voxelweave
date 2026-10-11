# CVPR rebuttal bank

## 1. “There is no method beyond adjacent difference or output PC.”

**Response.** This criticism is supported by the current evidence. Anchor-CV is demoted: it is cheap and strong but not uniquely informative. Three Plan7 method branches—minimum-influence context selection, multi-anchor jackknife dispersion and covariance-derived residualization—failed locked gates and were not retuned. The revised paper must be judged as a mechanism/findings contribution, not a superior-score paper.

**Submission consequence.** If the venue requires a new capability, the current paper should not be submitted as a main-track method paper.

## 2. “Finite-difference influence may be a perturbation artifact.”

**Response.** Across 0.5/1/2% amplitude, sign, Rademacher/Gaussian field and 1/2/4/8 directions, all 42 dataset--architecture strata pass the frozen rank-stability gate (minimum .942). Physical-plane pairs span .779–.954 and two of three plane gates fail. The revised claim is therefore perturbation-parameter robustness at a declared local plane, not plane-invariant influence.

## 3. “Overlap count and geometry already explain the effect.”

**Response.** Integer overlap is constant in the four one-shared-anchor contexts, yet continuous influence associates with error alignment/shared fraction on fastMRI and IXI after span, asymmetry and case controls. NingXia is mixed/null and explicitly falsifies universality. With two bracketing anchors, changing overlap while holding the complete physical distance set fixed is combinatorially impossible; this feasibility boundary is stated rather than hidden.

## 4. “The mechanism chain is called causal without identification.”

**Response.** It is not. Each arrow is a conditional association with a clustered interval, and the final context-level ranking arrow is weaker/heterogeneous. The manuscript prohibits causal mediation language and lists counterexamples.

## 5. “This duplicates the TMI paper.”

**Response.** The overlap audit assigns the physical intervention, endpoints/factors and operational QA to TMI; CVPR is limited to nonlinear shared-influence measurement, fixed-count tests and failed mechanism-derived methods. No audited TMI words remain in paragraph matches above the 0.45 diagnostic threshold after rewriting, but scientific overlap remains moderate-to-high because the CVPR capability gates failed. The current recommendation is **MERGE_OR_SEQUENCE_REQUIRED**, not simultaneous submission. Authors must disclose related work and follow both venues’ policies.
