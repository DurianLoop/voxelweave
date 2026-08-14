# TMI Claim Traceability

See also `SUPERSESSION_NOTICE.md` and `tables/ningxia_patient_cluster_corrections.json`. Historical NingXia intervals or permutations treating 22 series as independent are superseded by eight-patient clustering in the manuscript.

The authoritative numeric ledger is `EVIDENCE_LEDGER.md`. This file maps manuscript locations to code and machine-readable outputs.

| Claim | Manuscript location | Code | Configuration/procedure | Output |
|---|---|---|---|---|
| Shared consensus fraction | Sec. III/VI-A | `../../plan3_bias_diversity_decomposition.py` | x2/x4/x6, HAT/I3Net/SwinIR, exact MSE identity | `../../plan3_outputs/bias_diversity_summary.csv` |
| Zero vs maximal overlap | Sec. IV/VI-B | `../../plan4_disjoint_anchor_intervention.py`; `../../plan4_disjoint_ningxia.py`; `../../plan4_max_shared_control.py`; `../../plan4_overlap_levels_analysis.py` | x4 phase 0 vs 2; shared phase-0 mask; 5,000 case-cluster replicates | `../../plan4_outputs/overlap_zero_vs_max_summary.json` |
| Per-architecture replication | Sec. VI-C | same as above | HAT/SwinIR separately | same JSON and CSV |
| Analytical replication | Sec. VI-D | `../../plan4_analytical_disjoint.py` | linear/cubic; phase grids; target evaluation only | `../../plan4_outputs/analytical_disjoint_summary.json` |
| Raw diversity control | Sec. VI-E | `../../plan4_overlap_levels_analysis.py` | paired score magnitude and rank association | same JSON |
| Densification-benefit prediction | Sec. VI-F | `../../plan4_adaptive_acquisition_test.py`; `../../plan4_adaptive_baselines.py` | x4 score versus stored x4-x2 error gain; 5,000 case-cluster replicates | `../../plan4_outputs/adaptive_acquisition_summary.json`; `adaptive_acquisition_baselines.json` |
| PC versus flip-TTA | Sec. VI-G | `../../plan3_tta_joint_analysis.py` | 2 cohorts × 3 factors × 3 models; 2,000 clustered swaps | `../../plan3_outputs/tta_all_profiles.csv` |
| Curvature/spacing boundary | Discussion | `../../plan4_curvature_spacing_panel.py`; `../../plan4_curvature_spacing_analysis.py` | acquired anchors only; development/confirmation split | `../../plan4_outputs/curvature_spacing_summary.json` |
| Geometry and world-plane matching | Methods | `../../plan2_geometry_audit.py`; `../../FROZEN_METHOD.md` | affine origin match, tolerance 0.001 mm | `../../plan2_outputs/geometry_audit_summary.json` |

All paths are relative to this manuscript directory and point to immutable historical files. Examination identifiers are present in the corresponding per-case/per-plane CSVs.
