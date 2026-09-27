# Cross-architecture shared-evidence intervention

This is one of three frozen final-iteration analyses, on historically reused cohorts. All 20 ordered pairs of five frozen architecture implementations were evaluated separately on fastMRI (24 examinations) and IXI (115). The reference A(phase 0) is identical in the shared A0/B0 and disjoint A0/B2 conditions. There is no TTA in this experiment. Every target and common evaluation mask is identical across conditions. The mask is target-derived; this contrast is not acquired-only.

The primary endpoint averages five plane-level observable-fraction differences within an examination and then averages examinations. All 40 local intervals exclude zero under simultaneous 20-pair inference separately in each cohort: fastMRI gains 6.236–16.022 percentage points and IXI gains 13.113–28.531. Disagreement increases and alignment decreases in all pairs with their endpoint-specific simultaneous intervals excluding zero. These are related geometric endpoints, not three independent discoveries.

The ranking boundary remains material. All 20 fastMRI fixed-reference ranking intervals cross zero, including SAINT→I3Net with a negative point estimate (−.002609). IXI has 16 positive simultaneous fixed-reference ranking intervals and four crossing zero: HAT→I3Net, SwinIR→I3Net, SAINT→I3Net, CycleINR→I3Net. Condition-specific paired-error ranking is a different endpoint: 0/20 fastMRI and 20/20 IXI intervals exclude zero positively. Changing the error endpoint changes the conclusion; paired error is not silently substituted for fixed A-error.

This answers the objection that the original effect is only failure of same-network flip equivariance. It does not isolate acquisition identity from every nuisance: signed geometry, phase-specific normalization, companion accuracy and nonlinear response may change. Different models still share datasets/training objectives; these are ordered contrasts, not 40 independent replications. Five lineages do not establish all neural ensembles.

SAINT uses the physical target coordinate z/(source_depth−1) in both new phases. The correction and separate legacy reproduction were bound before new inference. All 695 legacy phase-0 wrapper outputs match the stored outputs exactly. That verification applies to legacy mapping; it does not imply corrected SAINT phase-0 equals its legacy prediction.

No pairs were excluded for result direction, no new significance threshold was selected, and no new score was fitted. The complete 200 endpoint rows, pointwise/simultaneous intervals, bootstrap seeds and raw arrays remain available.

## All primary and ranking contrasts

| dataset | pair | endpoint | delta | simultaneous_low | simultaneous_high |
| --- | --- | --- | --- | --- | --- |
| fastmri | hat__swinir | observable_gap | 0.160224 | 0.145968 | 0.17448 |
| fastmri | hat__i3net | observable_gap | 0.0975559 | 0.0875254 | 0.107586 |
| fastmri | hat__saint | observable_gap | 0.129614 | 0.116066 | 0.143162 |
| fastmri | hat__cycleinr | observable_gap | 0.115574 | 0.103371 | 0.127777 |
| fastmri | swinir__hat | observable_gap | 0.156744 | 0.143184 | 0.170304 |
| fastmri | swinir__i3net | observable_gap | 0.0864837 | 0.0745592 | 0.0984082 |
| fastmri | swinir__saint | observable_gap | 0.108526 | 0.0925006 | 0.124552 |
| fastmri | swinir__cycleinr | observable_gap | 0.110632 | 0.094129 | 0.127135 |
| fastmri | i3net__hat | observable_gap | 0.0889305 | 0.0763931 | 0.101468 |
| fastmri | i3net__swinir | observable_gap | 0.0774665 | 0.0641915 | 0.0907416 |
| fastmri | i3net__saint | observable_gap | 0.107007 | 0.0973571 | 0.116656 |
| fastmri | i3net__cycleinr | observable_gap | 0.0623596 | 0.0523212 | 0.072398 |
| fastmri | saint__hat | observable_gap | 0.126503 | 0.112446 | 0.14056 |
| fastmri | saint__swinir | observable_gap | 0.108459 | 0.0923437 | 0.124575 |
| fastmri | saint__i3net | observable_gap | 0.111273 | 0.10079 | 0.121756 |
| fastmri | saint__cycleinr | observable_gap | 0.0776502 | 0.0648442 | 0.0904563 |
| fastmri | cycleinr__hat | observable_gap | 0.112018 | 0.0946292 | 0.129407 |
| fastmri | cycleinr__swinir | observable_gap | 0.114916 | 0.0943511 | 0.135482 |
| fastmri | cycleinr__i3net | observable_gap | 0.0678299 | 0.0539214 | 0.0817384 |
| fastmri | cycleinr__saint | observable_gap | 0.0757888 | 0.0574589 | 0.0941186 |
| fastmri | hat__swinir | fixed_reference_ranking | 0.0330435 | -0.157182 | 0.223269 |
| fastmri | hat__i3net | fixed_reference_ranking | 0.013913 | -0.100396 | 0.128222 |
| fastmri | hat__saint | fixed_reference_ranking | 0.00173913 | -0.130618 | 0.134096 |
| fastmri | hat__cycleinr | fixed_reference_ranking | 0.0704348 | -0.118355 | 0.259224 |
| fastmri | swinir__hat | fixed_reference_ranking | 0.0165217 | -0.134812 | 0.167856 |
| fastmri | swinir__i3net | fixed_reference_ranking | 0.00869565 | -0.0904336 | 0.107825 |
| fastmri | swinir__saint | fixed_reference_ranking | 0.0026087 | -0.162991 | 0.168208 |
| fastmri | swinir__cycleinr | fixed_reference_ranking | 0.137391 | -0.149389 | 0.424172 |
| fastmri | i3net__hat | fixed_reference_ranking | 0.033913 | -0.109961 | 0.177787 |
| fastmri | i3net__swinir | fixed_reference_ranking | 0.033913 | -0.13869 | 0.206516 |
| fastmri | i3net__saint | fixed_reference_ranking | 0.0173913 | -0.0899362 | 0.124719 |
| fastmri | i3net__cycleinr | fixed_reference_ranking | 0.111304 | -0.116964 | 0.339573 |
| fastmri | saint__hat | fixed_reference_ranking | 0.0130435 | -0.100561 | 0.126647 |
| fastmri | saint__swinir | fixed_reference_ranking | 0.0365217 | -0.135969 | 0.209013 |
| fastmri | saint__i3net | fixed_reference_ranking | -0.0026087 | -0.115991 | 0.110774 |
| fastmri | saint__cycleinr | fixed_reference_ranking | 0.0278261 | -0.155723 | 0.211375 |
| fastmri | cycleinr__hat | fixed_reference_ranking | 0.0182609 | -0.109708 | 0.14623 |
| fastmri | cycleinr__swinir | fixed_reference_ranking | 0.0373913 | -0.139436 | 0.214219 |
| fastmri | cycleinr__i3net | fixed_reference_ranking | 0.0252174 | -0.0726283 | 0.123063 |
| fastmri | cycleinr__saint | fixed_reference_ranking | 0.00434783 | -0.0967775 | 0.105473 |
| fastmri | hat__swinir | paired_error_ranking | 0.0208696 | -0.159603 | 0.201342 |
| fastmri | hat__i3net | paired_error_ranking | 0.0408696 | -0.0935158 | 0.175255 |
| fastmri | hat__saint | paired_error_ranking | 0.00782609 | -0.0997412 | 0.115393 |
| fastmri | hat__cycleinr | paired_error_ranking | 0.0391304 | -0.081168 | 0.159429 |
| fastmri | swinir__hat | paired_error_ranking | 0.0286957 | -0.139884 | 0.197275 |
| fastmri | swinir__i3net | paired_error_ranking | 0.0286957 | -0.12041 | 0.177802 |
| fastmri | swinir__saint | paired_error_ranking | 0.0208696 | -0.147227 | 0.188966 |
| fastmri | swinir__cycleinr | paired_error_ranking | 0.0904348 | -0.125795 | 0.306665 |
| fastmri | i3net__hat | paired_error_ranking | 0.0426087 | -0.0978041 | 0.183021 |
| fastmri | i3net__swinir | paired_error_ranking | 0.0408696 | -0.130007 | 0.211746 |
| fastmri | i3net__saint | paired_error_ranking | 0.0173913 | -0.104239 | 0.139022 |
| fastmri | i3net__cycleinr | paired_error_ranking | 0.0469565 | -0.099321 | 0.193234 |
| fastmri | saint__hat | paired_error_ranking | 0.00869565 | -0.111018 | 0.128409 |
| fastmri | saint__swinir | paired_error_ranking | 0.0243478 | -0.12956 | 0.178256 |
| fastmri | saint__i3net | paired_error_ranking | 0.02 | -0.0934 | 0.1334 |
| fastmri | saint__cycleinr | paired_error_ranking | 0.0243478 | -0.0985225 | 0.147218 |
| fastmri | cycleinr__hat | paired_error_ranking | 0.0495652 | -0.075943 | 0.175073 |
| fastmri | cycleinr__swinir | paired_error_ranking | 0.101739 | -0.0890707 | 0.292549 |
| fastmri | cycleinr__i3net | paired_error_ranking | 0.0756522 | -0.0816601 | 0.232964 |
| fastmri | cycleinr__saint | paired_error_ranking | 0.033913 | -0.102468 | 0.170294 |
| ixi | hat__swinir | observable_gap | 0.285313 | 0.278187 | 0.292439 |
| ixi | hat__i3net | observable_gap | 0.183325 | 0.173211 | 0.193439 |
| ixi | hat__saint | observable_gap | 0.275462 | 0.268366 | 0.282558 |
| ixi | hat__cycleinr | observable_gap | 0.211967 | 0.205741 | 0.218193 |
| ixi | swinir__hat | observable_gap | 0.284858 | 0.277632 | 0.292085 |
| ixi | swinir__i3net | observable_gap | 0.182653 | 0.172503 | 0.192803 |
| ixi | swinir__saint | observable_gap | 0.281297 | 0.274057 | 0.288536 |
| ixi | swinir__cycleinr | observable_gap | 0.224018 | 0.217874 | 0.230163 |
| ixi | i3net__hat | observable_gap | 0.180013 | 0.169057 | 0.190968 |
| ixi | i3net__swinir | observable_gap | 0.179639 | 0.168739 | 0.19054 |
| ixi | i3net__saint | observable_gap | 0.179509 | 0.168405 | 0.190614 |
| ixi | i3net__cycleinr | observable_gap | 0.131126 | 0.121015 | 0.141238 |
| ixi | saint__hat | observable_gap | 0.274834 | 0.267769 | 0.281899 |
| ixi | saint__swinir | observable_gap | 0.280998 | 0.273899 | 0.288098 |
| ixi | saint__i3net | observable_gap | 0.182384 | 0.172124 | 0.192645 |
| ixi | saint__cycleinr | observable_gap | 0.225949 | 0.219799 | 0.232099 |
| ixi | cycleinr__hat | observable_gap | 0.211216 | 0.205557 | 0.216875 |
| ixi | cycleinr__swinir | observable_gap | 0.22334 | 0.217878 | 0.228802 |
| ixi | cycleinr__i3net | observable_gap | 0.13151 | 0.122267 | 0.140754 |
| ixi | cycleinr__saint | observable_gap | 0.225534 | 0.219909 | 0.23116 |
| ixi | hat__swinir | fixed_reference_ranking | 0.0282333 | 0.000812245 | 0.0556543 |
| ixi | hat__i3net | fixed_reference_ranking | 0.0248086 | -0.00346101 | 0.0530783 |
| ixi | hat__saint | fixed_reference_ranking | 0.0334017 | 0.00245666 | 0.0643468 |
| ixi | hat__cycleinr | fixed_reference_ranking | 0.0445909 | 0.0110106 | 0.0781711 |
| ixi | swinir__hat | fixed_reference_ranking | 0.0278229 | 0.00101858 | 0.0546273 |
| ixi | swinir__i3net | fixed_reference_ranking | 0.0239249 | -0.00306145 | 0.0509112 |
| ixi | swinir__saint | fixed_reference_ranking | 0.0310108 | 0.00332636 | 0.0586953 |
| ixi | swinir__cycleinr | fixed_reference_ranking | 0.0444646 | 0.0125988 | 0.0763304 |
| ixi | i3net__hat | fixed_reference_ranking | 0.0500118 | 0.00165599 | 0.0983677 |
| ixi | i3net__swinir | fixed_reference_ranking | 0.0485994 | 0.00245481 | 0.094744 |
| ixi | i3net__saint | fixed_reference_ranking | 0.0533654 | 0.00395643 | 0.102774 |
| ixi | i3net__cycleinr | fixed_reference_ranking | 0.0579184 | 0.0082688 | 0.107568 |
| ixi | saint__hat | fixed_reference_ranking | 0.0312791 | 0.00181557 | 0.0607426 |
| ixi | saint__swinir | fixed_reference_ranking | 0.0296852 | 0.00296029 | 0.05641 |
| ixi | saint__i3net | fixed_reference_ranking | 0.0274363 | -0.00221781 | 0.0570904 |
| ixi | saint__cycleinr | fixed_reference_ranking | 0.0395013 | 0.0104782 | 0.0685244 |
| ixi | cycleinr__hat | fixed_reference_ranking | 0.0288093 | 0.00350899 | 0.0541096 |
| ixi | cycleinr__swinir | fixed_reference_ranking | 0.0297483 | 0.00524404 | 0.0542525 |
| ixi | cycleinr__i3net | fixed_reference_ranking | 0.0253137 | -0.00125319 | 0.0518805 |
| ixi | cycleinr__saint | fixed_reference_ranking | 0.0258345 | 0.0029772 | 0.0486917 |
| ixi | hat__swinir | paired_error_ranking | 0.0303322 | 0.00392429 | 0.0567401 |
| ixi | hat__i3net | paired_error_ranking | 0.0357926 | 0.00228078 | 0.0693045 |
| ixi | hat__saint | paired_error_ranking | 0.0337963 | 0.00403501 | 0.0635575 |
| ixi | hat__cycleinr | paired_error_ranking | 0.0387832 | 0.00918432 | 0.0683822 |
| ixi | swinir__hat | paired_error_ranking | 0.0303559 | 0.0040514 | 0.0566604 |
| ixi | swinir__i3net | paired_error_ranking | 0.0348773 | 0.0030291 | 0.0667255 |
| ixi | swinir__saint | paired_error_ranking | 0.0320051 | 0.00511436 | 0.0588957 |
| ixi | swinir__cycleinr | paired_error_ranking | 0.0389568 | 0.0107445 | 0.0671692 |
| ixi | i3net__hat | paired_error_ranking | 0.0370552 | 0.00320748 | 0.0709028 |
| ixi | i3net__swinir | paired_error_ranking | 0.0359899 | 0.00354848 | 0.0684313 |
| ixi | i3net__saint | paired_error_ranking | 0.0401483 | 0.00486349 | 0.0754332 |
| ixi | i3net__cycleinr | paired_error_ranking | 0.0380099 | 0.00505284 | 0.070967 |
| ixi | saint__hat | paired_error_ranking | 0.034175 | 0.00444395 | 0.0639061 |
| ixi | saint__swinir | paired_error_ranking | 0.032439 | 0.00535075 | 0.0595273 |
| ixi | saint__i3net | paired_error_ranking | 0.0384676 | 0.00351657 | 0.0734186 |
| ixi | saint__cycleinr | paired_error_ranking | 0.0345064 | 0.00823051 | 0.0607824 |
| ixi | cycleinr__hat | paired_error_ranking | 0.0376864 | 0.00978559 | 0.0655873 |
| ixi | cycleinr__swinir | paired_error_ranking | 0.0386649 | 0.0119221 | 0.0654076 |
| ixi | cycleinr__i3net | paired_error_ranking | 0.0360688 | 0.00535728 | 0.0667803 |
| ixi | cycleinr__saint | paired_error_ranking | 0.0333149 | 0.00894213 | 0.0576877 |
