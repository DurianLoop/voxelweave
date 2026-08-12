from __future__ import annotations

import csv
import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
RASINET_ROOT = REPO_ROOT / "design" / "rasinet"


def _read(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate() -> dict[str, object]:
    output = RASINET_ROOT / "outputs" / "icassp_primary"
    summary = _read(output / "summary.csv")
    per_case = _read(output / "per_case.csv")
    manifests = _read(output / "input_manifest.csv")
    expected_cases = {"full_test115": 115, "fastmri_full": 24, "ningxia_cv": 22}
    expected_targets = {
        "full_test115": {"i3net", "hat", "swinir", "acsinet"},
        "fastmri_full": {"i3net", "hat", "swinir"},
        "ningxia_cv": {"i3net", "hat", "swinir"},
    }
    failures: list[str] = []
    if len(summary) != 504:
        failures.append(f"expected 504 summary groups, found {len(summary)}")
    if len(per_case) != 33672:
        failures.append(f"expected 33672 per-examination rows, found {len(per_case)}")
    if len(manifests) != 161:
        failures.append(f"expected 161 input manifests, found {len(manifests)}")
    for row in manifests:
        if row.get("affine_aligned") != "1":
            failures.append(f"affine mismatch in manifest: {row.get('profile')} {row.get('case')}")
        if int(row.get("generated_slices", "0")) <= 0:
            failures.append(f"missing generated slices in manifest: {row.get('profile')} {row.get('case')}")
    for row in summary:
        if int(row["cases"]) != expected_cases[row["profile"]]:
            failures.append(f"incomplete group: {row['profile']} {row['target']} {row['analysis']} {row['subset_id']}")
        if row["target"] in row["committee"].split(";"):
            failures.append(f"target leaked into committee: {row['profile']} {row['target']} {row['committee']}")
    primary = [
        row
        for row in summary
        if row["analysis"] == "score_variants"
        and row["score"] == "target_abs_median"
        and row["mask"] == "target_0.01"
        and row["normalization"] == "raw"
        and row["subset_id"] == "full"
    ]
    if len(primary) != 10:
        failures.append(f"expected ten primary profiles, found {len(primary)}")
    for profile, targets in expected_targets.items():
        actual = {row["target"] for row in primary if row["profile"] == profile}
        if actual != targets:
            failures.append(f"primary target mismatch for {profile}: {sorted(actual)}")

    table = (RASINET_ROOT / "paper" / "tables_icassp" / "table_main.tex").read_text(encoding="utf-8")
    table_rows = len(re.findall(r"^(IXI|fastMRI-brain|NingXia)\s*&", table, flags=re.MULTILINE))
    if table_rows != 10:
        failures.append(f"expected ten generated main-table rows, found {table_rows}")
    papers = [
        RASINET_ROOT / "paper" / "paper_icassp_regular.tex",
        RASINET_ROOT / "paper" / "paper_icassp_extended.tex",
    ]
    forbidden = (
        "corrected target-specific",
        "external cross-validation cohort",
        "certified uncertainty",
        "calibrated uncertainty probability",
        "todo:",
    )
    for paper in papers:
        text = paper.read_text(encoding="utf-8").lower()
        for phrase in forbidden:
            if phrase in text:
                failures.append(f"forbidden phrase in {paper.name}: {phrase}")

    registry = _read(RASINET_ROOT / "outputs" / "results_registry.csv")
    experiment_ids = [row["experiment_id"] for row in registry]
    if len(experiment_ids) != len(set(experiment_ids)):
        failures.append("duplicate experiment IDs in results registry")
    if len(registry) != 5631:
        failures.append(f"expected 5631 registry rows, found {len(registry)}")
    for path in {row["output_file"] for row in registry}:
        if not Path(path).is_file():
            failures.append(f"registry output does not exist: {path}")

    stress = _read(RASINET_ROOT / "outputs" / "shared_error_stress" / "summary.csv")
    if len(stress) != 30 or any(int(row.get("number_of_cases", "0")) != 20 for row in stress):
        failures.append("shared-error stress summary is not a 20-examination clustered analysis")
    tta = _read(RASINET_ROOT / "outputs" / "tta_fastmri_unified" / "summary.csv")
    if len(tta) != 1 or int(tta[0].get("cases", "0")) != 24:
        failures.append("TTA summary does not contain all 24 fastMRI-brain examinations")
    analytical = _read(RASINET_ROOT / "outputs" / "analytical_cost" / "per_case.csv")
    if len(analytical) != 60 or len({(row["profile"], row["case"]) for row in analytical}) != 30:
        failures.append("analytical benchmark is not 30 examinations x two methods")
    posthoc = _read(RASINET_ROOT / "outputs" / "posthoc_cost" / "per_case.csv")
    if len(posthoc) != 30 or any(row.get("target") != "swinir" for row in posthoc):
        failures.append("post-hoc benchmark is not the fixed 30-examination SwinIR audit")
    result = {
        "passed": not failures,
        "failures": failures,
        "summary_groups": len(summary),
        "per_examination_rows": len(per_case),
        "input_manifests": len(manifests),
        "primary_profiles": len(primary),
        "registry_rows": len(registry),
        "stress_summary_rows": len(stress),
        "tta_cases": int(tta[0]["cases"]) if tta else 0,
        "analytical_cost_rows": len(analytical),
        "posthoc_cost_rows": len(posthoc),
    }
    (RASINET_ROOT / "outputs" / "icassp_validation.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    report = [
        "# ICASSP Output Consistency",
        "",
        f"- Status: {'PASS' if result['passed'] else 'FAIL'}",
        f"- Summary groups: {len(summary)} / 504",
        f"- Per-examination rows: {len(per_case)} / 33672",
        f"- Input manifests: {len(manifests)} / 161",
        f"- Primary dataset--target profiles: {len(primary)} / 10",
        f"- Registry rows: {len(registry)}",
        "",
    ]
    if failures:
        report.extend(["## Failures", ""] + [f"- {failure}" for failure in failures])
    else:
        report.append("All predefined profiles, target exclusions, generated main-table rows, and registry identities are consistent.")
    (RASINET_ROOT / "paper" / "consistency_report_icassp.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    report = validate()
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["passed"] else 1)
