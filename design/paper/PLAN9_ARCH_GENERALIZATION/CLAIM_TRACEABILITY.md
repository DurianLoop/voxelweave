# Plan-9 claim traceability

| Final claim | Direct evidence | Status / boundary |
|---|---|---|
| Physical-context dependence changes local error observability across architecture families | `outputs/p9_architecture_forest.csv`; `figures/p9_architecture_forest.pdf` | Supported at fastMRI x4 for HAT, SwinIR, I3Net, SAINT, CycleINR; all observable-gain CIs exclude zero. |
| Examination-level ranking benefit is architecture-heterogeneous | `outputs/p9_architecture_forest.csv` | Supported: CycleINR positive; I3Net and SAINT intervals include zero. Do not claim universal ranking improvement. |
| A stable new-architecture influence probe exists | `outputs/p9_influence_stability.csv`; `outputs/p9_influence_verdict.json` | Supported only for SAINT under the frozen epsilon gate. |
| Influence universally beats shared-count across architectures | `outputs/p9_influence_clustered_inference.csv`; `outputs/p9_influence_clustered_verdict.json` | Falsified/unsupported: SAINT beyond-count and fixed-count intervals cross zero; I3Net and CycleINR fail stability gates. |
| Architecture diversity does not imply examination-level error independence | `outputs/p9_cross_arch_error_rank_correlations.csv`; `outputs/p9_consensus_error_intersection.csv` | Supported on recovered common support; median case-error rank correlations are high and top-error cases overlap. |
| Architecture diversity can still increase local pixel-error diversity | `outputs/p9_error_correlation_pair_types.csv`; `outputs/p9_cross_arch_prediction_error_diversity_summary.csv` | Supported descriptively on fastMRI x4. |
| P0 models are not broken local baselines | `outputs/p9_reconstruction_benchmark.csv`; `RECONSTRUCTION_BENCHMARK_REPORT.md` | Supported: finite for all 24 fastMRI cases and each beats Linear under the common x4 protocol. |
| Five-architecture mechanism law holds across x2/x4/x6 | `FACTOR_ARCHITECTURE_ANALYSIS.md` | Not identifiable and not claimed. Cross-factor evidence is reconstruction-only; the same-target mechanism comparison is x4-only. |

## Implementation provenance

- I3Net: official-architecture lineage, locally trained; no official checkpoint.
- SAINT: adapted local SAINT-style implementation; not exact official repository/weights.
- CycleINR: internal CycleINR-style training using the local ArSSRNet path; not an exact official reproduction.
- HAT/SwinIR: retained Plan-8 reference architectures.

Every manuscript statement should be interpreted together with these provenance limits and the protocol amendment recorded in `PROTOCOL_AMENDMENT_001.md`.
