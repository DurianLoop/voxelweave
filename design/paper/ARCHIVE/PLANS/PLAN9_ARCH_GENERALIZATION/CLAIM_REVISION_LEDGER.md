# Plan-9 claim revision ledger

| Candidate claim | Evidence | Decision |
|---|---|---|
| Measurement-disjoint contexts expose more paired error across evaluated interpolation paradigms | Observable gain is positive with clustered CI above zero for HAT, SwinIR, I3Net, SAINT, CycleINR | **Supported** |
| Examination-level error ranking always improves when contexts are disjoint | Ranking delta positive for HAT/SwinIR/I3Net/CycleINR but significant only for CycleINR; SAINT point estimate is negative | **Falsified as universal** |
| Local Physical Measurement Influence is stable across all evaluated architectures | SAINT passes all gates; I3Net and CycleINR fail amplitude and/or sign gates | **Falsified as universal** |
| Stable shared influence aligns error in a non-transformer architecture | SAINT broad influence--alignment rho .706 [.680,.734]; fixed-count partial rho .063 [-.021,.149] | **Direction supported; fixed-count precision insufficient** |
| Influence universally beats raw overlap count | SAINT error-cosine advantage .014 with CI crossing zero; I3Net is negative and claim-ineligible; CycleINR positive but claim-ineligible | **Falsified as universal** |
| Architectural diversity automatically yields independent errors | Case-level rank correlations remain high; fastMRI median pair rho .945--.981 across factors | **Falsified** |
| Architecturally distant pairs can increase local error diversity | CycleINR--I3Net median pixel error cosine .564 vs HAT--SwinIR .918 at fastMRI x4 | **Supported descriptively** |
| One family drives the observable-gain result | Equal-family observable gain remains positive after leaving out each family | **Not supported; leave-one-family-out robust** |

