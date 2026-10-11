# Factor × architecture analysis and identifiability boundary

`outputs/p9_factor_architecture_interaction.csv` reports the common-support reconstruction interaction for x2/x4/x6. Reconstruction error increases with factor for every representative neural architecture, but the rate is heterogeneous: SAINT degrades least in relative MAE, while I3Net remains best in absolute MAE yet has the largest x6/x2 ratio.

The requested five-architecture *mechanism* interaction is not fully identifiable from the recovered bank. The preregistered same-target complementary x4 phase grids require four phase-2 anchors; an equivalent integer-target disjoint construction does not exist for complementary x2 phase grids, and complete compatible x6 CycleINR/SAINT mechanism contexts are unavailable. Creating unequal-spacing or padded contexts would change the estimand and violate protocol fairness.

Accordingly:

- x2/x4/x6 support a reconstruction difficulty × architecture result;
- prior analytical evidence supports worsening consensus blindness with factor;
- the five-neural-architecture shared/observable and disjoint-benefit result is explicitly limited to x4;
- no cross-architecture neural factor law is claimed.

This is a design-support limitation, not a missing favorable analysis.

