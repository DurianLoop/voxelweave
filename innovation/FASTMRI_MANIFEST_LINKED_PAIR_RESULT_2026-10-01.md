# Manifest-linked multi-T2 candidate screen: nonpixel result

The [crosswalk plan](FASTMRI_MANIFEST_UID_CROSSWALK_PLAN_2026-10-01.md) was frozen before reading manifest pointers. Its [anonymous output](experiments/fastmri_manifest_uid_crosswalk/summary.json) shows that 138 `is_t2=True` manifest rows in the 61 selected cases refer to 122 distinct DICOM SeriesInstanceUIDs: 16 rows repeat a UID across 12 cases. Among those 122 referenced UIDs, 67 have a DICOM description containing literal `T2` and 55 do not. The latter are **unlabeled by this literal rule**, not proven non-T2-weighted sequences. Four additional literal-T2 DICOM UID series in the full folders were not pointed to by those manifest T2 rows. This explains why the first [DICOM-label screen](FASTMRI_ALL_T2_HEADER_GATE_RESULT_2026-10-01.md) could not stand for all manifest-linked candidates.

The subsequent [frozen pair rule](FASTMRI_MANIFEST_LINKED_PAIR_PLAN_2026-10-01.md) therefore compared every pair of distinct manifest-linked UIDs in each case without requiring a literal DICOM T2 label. Its [full anonymous output](experiments/fastmri_manifest_linked_pair_gate/summary.json) used 2,944 nonpixel DICOM headers and reports:

| Manifest-linked pairs | Count |
|---|---:|
| Total | 64 |
| Both / one / neither UID literal-T2-labeled | 9 / 53 / 2 |
| Physical slice centers matched within 0.1 mm | 57 |
| Full checked geometry/protocol/identity match, excluding time | 4 |
| Usable distinct acquisition/series timing | **0** |
| Independently acquired raw planes proven | **0** |

All 64 pairs lack usable timing under the frozen rule. All four technical matches are the same anonymous pairs found in the literal-DICOM-label screen: `candidate_01`/1--2, `candidate_05`/2--3, `candidate_43`/1--2 and `candidate_45`/1--5. None of the 55 pairs with fewer than two literal T2 labels adds a technical match. The two screens overlap but have different selection rules; they must not be counted as independent evidence. `ORIGINAL/PRIMARY` and `2D` are descriptive headers, not proof of raw independent measurements. No image pixel, weight, locked test data or GPU was used.

Crosswalk plan/script/result SHA-256: `76E8F5FB9F283CDC9613BA967BF2A209E060926E69C5D387B08E2746FEDDB78E`, `0B1FBAF4CF43978FB8350F111E0C1988A987CD17D0FAF2EE6CF120F6E9C1F5A2`, `C8F0564955077C1D87D888DCB32FB5824BE1A916A14A9AA62F70185152A141B5`. Pair plan/script/result SHA-256: `AA2ACB6574E2FE1AF383EDB844E23D288DF8D4C306944ACC6EEAA7DC268423E0`, `308FCE9ACDBFD16E3C17194FFE2B4862D9D9DE5DE6CCD7D9F0909F8B78BF29F5`, `2D4971497173F09EF29AB64C57B96BCB405963D3A6846B1F41DEA7E16B4B668D`. Outputs contain only anonymous ordinals, counts, scalar differences and reason codes.

**Decision.** Literal-label undercoverage did not hide a new technically matched pair in the manifest-linked candidate set. The four pairs remain only source trace-back leads. Establish the exact local release and publication rights, reconcile sequence classification and obtain independent-acquisition records before considering a separately frozen pixel-stage experiment. This local dataset remains outside the public-only manuscript.
