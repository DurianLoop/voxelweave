# Post-hoc integrity sensitivity: remove self-comparisons

During final source review, the HAT/SwinIR broad-grid aggregation was found to include the reference-versus-itself rows (overlap 2, influence 1, error cosine 1). This changes interpretation of the broad association. The main fixed-one-overlap result already excludes them.

One mandatory sensitivity is added to address this concrete audit finding: remove all reference self-pairs (overlap_count=2), recompute error-alignment Spearman for count and influence, and their paired absolute-correlation difference in every cohort/model. Use 5,000 examination/patient bootstrap draws, seed 20260911, pointwise and six-stratum simultaneous intervals. Retain all strata and all signs. This is explicitly post-hoc; it does not restart score search or create another primary hypothesis. Original summaries and figures remain preserved in the supplement and snapshot.
