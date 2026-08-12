from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PAPER_ROOT = REPO_ROOT / "design" / "rasinet" / "paper"


def _read_csv(path: Path) -> list[dict]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def check_main_table_values(rows: list[dict], tex: str) -> list[str]:
    errors: list[str] = []
    for row in rows:
        expected = (
            f"{float(row['PixelCorrFG']):.3f}",
            f"{float(row['CaseSpearman']):.3f}",
            f"{float(row['NormalizedAURC']):.3f}",
            f"{100.0 * float(row['RRR50']):.1f}\\%",
        )
        for value in expected:
            if value not in tex:
                errors.append(
                    f"main table is missing formatted value {value} for {row['Dataset']}/{row['Target']}"
                )
    return errors


def check_manuscript_claims(tex: str) -> list[str]:
    errors: list[str] = []
    for forbidden in ("smoke", "mini"):
        if re.search(rf"\b{forbidden}\b", tex, flags=re.IGNORECASE):
            errors.append(f"manuscript contains forbidden screening-profile claim: {forbidden}")
    for line in tex.splitlines():
        lowered = line.lower()
        if "calibrated probability" in lowered and not any(
            boundary in lowered
            for boundary in ("not a calibrated probability", "neither a calibrated probability")
        ):
            errors.append("manuscript incorrectly describes the reliability score as a calibrated probability")
    return errors


def check_latex_log(log: str) -> list[str]:
    patterns = (
        r"LaTeX Error",
        r"Fatal error",
        r"undefined references",
        r"Citation .* undefined",
        r"Reference .* undefined",
        r"Overfull \\hbox",
    )
    return [f"LaTeX log matches error pattern: {pattern}" for pattern in patterns if re.search(pattern, log, re.IGNORECASE)]


def run_checks(require_log: bool = True) -> list[str]:
    required = (
        PAPER_ROOT / "main.tex",
        PAPER_ROOT / "supplement.tex",
        PAPER_ROOT / "references.bib",
        PAPER_ROOT / "tables" / "table_committee_main.csv",
        PAPER_ROOT / "tables" / "table_committee_main.tex",
        PAPER_ROOT / "tables" / "supp_table_main_ci.tex",
        PAPER_ROOT / "figures" / "figure1_framework_compact.pdf",
        PAPER_ROOT / "figures" / "figure2_committee_risk.pdf",
        PAPER_ROOT / "figures" / "figure3_committee_composition.pdf",
        PAPER_ROOT / "figures" / "figure4_committee_qualitative.pdf",
        PAPER_ROOT / "asset_source_manifest.csv",
    )
    errors = [f"missing required artifact: {path}" for path in required if not path.exists()]
    if errors:
        return errors
    main_tex = (PAPER_ROOT / "main.tex").read_text(encoding="utf-8")
    errors.extend(check_manuscript_claims(main_tex))
    table_rows = _read_csv(PAPER_ROOT / "tables" / "table_committee_main.csv")
    table_tex = (PAPER_ROOT / "tables" / "table_committee_main.tex").read_text(encoding="ascii")
    errors.extend(check_main_table_values(table_rows, table_tex))
    if require_log:
        for log_name in ("main.log", "supplement.log"):
            log_path = PAPER_ROOT / log_name
            if not log_path.exists():
                errors.append(f"missing LaTeX log: {log_path}")
            else:
                errors.extend(check_latex_log(log_path.read_text(encoding="utf-8", errors="replace")))
    return errors


def write_report(errors: list[str]) -> Path:
    report_path = PAPER_ROOT / "consistency_report.md"
    lines = ["# Paper Consistency Report", ""]
    if errors:
        lines.extend(["Status: FAIL", "", *[f"- {error}" for error in errors]])
    else:
        lines.extend(["Status: PASS", "", "All required artifacts, manuscript claim guards, generated table values, and LaTeX log checks passed."])
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Check compact paper artifacts and numeric consistency.")
    parser.add_argument("--skip-log", action="store_true")
    args = parser.parse_args()
    errors = run_checks(require_log=not args.skip_log)
    report = write_report(errors)
    print(f"Wrote {report}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print("Paper consistency checks passed.")


if __name__ == "__main__":
    main()
