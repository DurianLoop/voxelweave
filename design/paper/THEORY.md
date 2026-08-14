# Target-Preserving Context Consistency: Formal Interpretation

Let `y_p` be the unknown target at physical plane `p`, and let `f_s(p)=f(x_s,p)` be a deterministic reconstruction under sampling context `s`. For a metric `d`, define context discrepancy

`Delta(s1,s2,p) = d(f_s1(p), f_s2(p))`.

By the triangle inequality,

`Delta <= d(f_s1,y_p) + d(f_s2,y_p)`.

Therefore,

`max(d(f_s1,y_p), d(f_s2,y_p)) >= Delta/2`.

This is a one-sided statement: large disagreement implies at least one reconstruction has error at least half the disagreement. It does not identify which reconstruction is wrong and does not upper-bound either error.

The converse is false. For any large error `e`, choose `f_s1=f_s2=z` with `d(z,y_p)=e`; then `Delta=0` while both reconstructions are wrong. The controlled shared-blur experiment instantiates this consistent-but-wrong regime empirically.

For a family of contexts `S`, useful reliability requires an error-diversity condition: difficult inputs must cause at least some admissible contexts to separate. If the reconstruction operator is contractive toward the same biased solution for all contexts, consistency becomes anti-informative.

Intensity scaling matters because `d` is not invariant to arbitrary affine intensity transformations. A shared positive scaling preserves ranking within a case, while independent factor normalization changes the geometry of `d`. Thus the deployment contract must specify a common physical intensity representation or use a separately validated shared normalization.

This formalization supports the term **target-preserving context consistency** as a class of one-sided witnesses. Current experiments validate only the sampling-factor instance; they do not establish the full framework for arbitrary perturbations.

