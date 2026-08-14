# TMI rebuttal bank

## 1. “The theory is elementary.”

**Response.** We agree that the identity cancelling shared error is elementary and do not claim it as new. The contribution is the controlled, same-target manipulation of a recorded MRI acquisition variable—physical slice-anchor reuse—and its connection to aligned reconstruction error, suppressed observability, endpoint/factor dependence and examination-level selective QA across three cohorts. The revised manuscript states this boundary in the introduction and discussion and cites prior systematic-error and leave-one-slice-out work.

**Evidence already present.** P6-E01/E02/E03/E11/E12; ten-paper collision matrix.  
**Do not promise later.** A prospective matched-order acquisition is not available; it is a limitation.

## 2. “The shared control reverses order, so overlap is not identified.”

**Response.** Correct. The reversal preserves target and anchor identity but changes order, and the manuscript calls it a paired intervention with a residual order-equivariance confound. Exact geometry rules out physical mismatch but not ordering. The conclusion is directional and supported by analytical factors and the separate conference clean-control audit; we do not claim a pure causal coefficient.

**Evidence.** Geometry audit over 322 outputs; matched plane/mask/model pairing.  
**Unavailable now.** Prospective complementary interleaved phases with an order-symmetric model.

## 3. “Why does this matter without clinical validation?”

**Response.** The intended consequence is technical reconstruction QA, not diagnosis. At 70% IXI coverage, disjoint scoring retained 0/29 prespecified high-error examinations versus 2/1/3 under shared/committee/adjacent scores; fastMRI was 0 versus 1/0/1, while eight-patient NingXia was uncertain. The effect disappears at high coverage because most cases must be retained. We removed patient-safety language and state that reader/pathology validation is future work.

## 4. “The result is metric-specific.”

**Response.** All 42 disjoint-minus-shared point differences across seven endpoints/two models/three cohorts are positive, but absolute SSIM ranking is weak in fastMRI/NingXia. A prespecified low-frequency-versus-structural mechanism contrast also changed sign across cohorts and is reported as falsified. The supported claim is robust for intensity-domain error, not metric independence.

## 5. “The proposed QA is too expensive or unavailable.”

**Response.** We now report calls, measured latency, storage and information assumptions. Disjoint scoring is appropriate when complementary phase-grid reconstructions already exist and intermediate-coverage review matters. When they do not, adjacent-anchor MAE/Anchor-CV are zero-neural-call defaults; adjacent MAE is strongest on NingXia. We do not recommend universal deployment.

