# Frozen qualitative selection rule

Frozen: 2026-08-14, before inspecting candidate images.

The qualitative panel is selected only from the 24-case fastMRI x4 same-target experiment and only from the three P0 architectures (I3Net, SAINT, CycleINR).

1. Within each model and the shared-control condition, rank all 120 case-plane observations by paired error (descending) and prediction disagreement (ascending).
2. Mark a model-specific stable-wrong observation when it lies in the top error quartile and bottom disagreement quartile using the already frozen thresholds in the primary script.
3. For each common case-plane, count model-specific stable-wrong marks.
4. Select the observation with the largest count; ties are broken by the largest mean error percentile, then the smallest case identifier and target index.
5. If the maximum count is zero, the panel is explicitly labelled a high-error example rather than stable-wrong evidence; the same tie-break rule is used.

The panel displays the target, one reference prediction, reference absolute error, shared-control disagreement, and disjoint-context disagreement for every P0 model. No image appearance enters selection.

