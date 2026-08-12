# Cross-Scale Physical Alignment Audit

Array depth is not used as the feasibility criterion. For every case, scale, and target, the physical origin of slice index `z` is computed as `affine[:3,3] + affine[:3,2] * z`. Generated planes are matched only when their world-coordinate origins differ by at most 0.001 mm and both planes are generated at their respective scales.

- Pair records: 1518
- Physically matched records: 1518
- Unmatched records: 0
- Scale pairs: ×2/×4, ×2/×6, ×4/×6.
- Observed anchors are excluded before matching.
- Different array depths restrict the shared physical extent but do not by themselves make matching impossible.
- No interpolation or post-validation resampling is used.

Example-level coordinates, affine deltas, shapes, matched-plane counts, and consistency values are stored in `cross_scale_physical_pair_scores.csv`.
