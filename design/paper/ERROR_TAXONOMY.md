# Quantitative Error Taxonomy

| Category | Quantitative signature | Detected by | Missed by | Supported mechanism | Mitigation / next evidence |
|---|---|---|---|---|---|
| Context-sensitive error | high cross-factor separation and target error | PC/local PC | none by definition | intervention-dependent output component | review; use valid physical contexts |
| Shared consensus error | consensus MSE: 80.9% fastMRI, 86.5% NingXia | target retrospectively; partly anchor change | PC and model disagreement | shared anchors and inductive biases | heterogeneous measurement/intervention or input witness |
| Shared-anchor stable-wrong | low-PC/high-error; x4–x6 first position delta 0.147 [0.030,0.286] | anchor change catches 6/14 | PC | shared left anchor plus nonlinear target trajectory | position/anchor-aware warning; new-site confirmation |
| Nonlinear through-plane anatomy | high target deviation from linear anchor path; error rho 0.58–0.97 | anchor change proxy; target curvature retrospectively | simple factor label | rapid inter-slice structural change | validate normalized context feature |
| Sampling-distance error | x2 < x4 < x6 in 138/138 units | factor/geometry known before inference | scalar triangle attribution adds nothing | larger missing distance | acquisition-aware risk prior |
| Architecture-invariant difficulty | neural error rho median 0.961 fastMRI; six-method 0.991 IXI | peer consensus, input scale/change | architecture selection | common task/measurement limitation | focus on data/context rather than module search |
| Architecture-specific residual | 10.3% architecture effect fastMRI, 0.6% NingXia | model identity/disagreement | case-only predictors | inductive-bias residual | model-specific audit where material |
| Intensity-scale error | raw range predicts raw MAE strongly | raw PC/input range | normalized endpoint | same-unit MAE scaling | report normalized and raw endpoints |
| Low-frequency/structural error | low-band rho 0.817/0.722 | low-band PC | high-pass-only witness | broad structural/intensity mismatch | multi-band reporting |
| High-frequency error | high-band rho 0.791/0.637; NingXia pixel rho 0.192 | partly high-band PC | raw agreement can conceal it | shared smoothing/detail loss | edge-specific independent witness |
| Motion/registration residual | weak translation rho ~0.15; registration residual heterogeneous | registration proxy | raw factor labels | possibly site-specific, not global | retain only as NingXia candidate |

