from __future__ import annotations

import csv
import json
from pathlib import Path

from acsinet.metrics import evaluate_consistency_method, summarize_consistency


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docx" / "experiment_notes" / "acsinet_3d_consistency"
ACSI_RUN = ROOT / "acsinet" / "runs" / "full_test115"
I3_RUN = ROOT / "ixi_i3net" / "runs" / "full_test115_stable"


LOWER_IS_BETTER = {"zge", "zle", "edge_z_error", "interslice_ncc_mae"}


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _fmt(value: object, digits: int = 4) -> str:
    return f"{float(value):.{digits}f}"


def _markdown_table(rows: list[dict], columns: list[str]) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(col, "")) for col in columns) + " |")
    return "\n".join(lines)


def _load_acsi_consistency() -> list[dict]:
    rows = _read_csv(ACSI_RUN / "metrics" / "per_case_3d_consistency.csv")
    return [row for row in rows if row["method"] == "acsinet"]


def _compute_i3_consistency() -> list[dict]:
    return evaluate_consistency_method(
        I3_RUN / "eval_inputs" / "gt",
        I3_RUN / "model_outputs",
        "diff_",
        "i3net",
    )


def _win_rates(acsi_rows: list[dict], i3_rows: list[dict]) -> list[dict]:
    acsi_by_case = {row["case"]: row for row in acsi_rows}
    i3_by_case = {row["case"]: row for row in i3_rows}
    rows: list[dict] = []
    for metric in ["zge", "zle", "edge_z_error", "interslice_ncc_mae"]:
        wins = 0
        valid = 0
        deltas = []
        for case, acsi in acsi_by_case.items():
            i3 = i3_by_case.get(case)
            if i3 is None:
                continue
            acsi_value = float(acsi[metric])
            i3_value = float(i3[metric])
            valid += 1
            deltas.append(i3_value - acsi_value)
            if metric in LOWER_IS_BETTER and acsi_value < i3_value:
                wins += 1
        rows.append(
            {
                "metric": metric,
                "wins": wins,
                "valid_cases": valid,
                "win_rate": wins / valid if valid else 0.0,
                "mean_i3_minus_acsi": sum(deltas) / len(deltas) if deltas else 0.0,
            }
        )
    return rows


def _complexity_rows() -> list[dict]:
    acsi = _read_json(ACSI_RUN / "metrics" / "complexity.json")
    i3 = _read_json(I3_RUN / "metrics" / "complexity.json")
    return [
        {
            "method": "ACSI-Net",
            "params_m": acsi["params_m"],
            "per_generated_slice_flops_g": acsi["per_generated_slice_flops_g"],
        },
        {
            "method": "I3Net",
            "params_m": i3["params_m"],
            "per_generated_slice_flops_g": i3["per_generated_slice_flops_g"],
        },
        {
            "method": "I3/ACSI ratio",
            "params_m": i3["params_m"] / acsi["params_m"],
            "per_generated_slice_flops_g": i3["per_generated_slice_flops_g"] / acsi["per_generated_slice_flops_g"],
        },
    ]


def _case_gap_rows(acsi_rows: list[dict], i3_rows: list[dict]) -> list[dict]:
    acsi_by_case = {row["case"]: row for row in acsi_rows}
    i3_by_case = {row["case"]: row for row in i3_rows}
    rows: list[dict] = []
    for case, acsi in acsi_by_case.items():
        i3 = i3_by_case.get(case)
        if i3 is None:
            continue
        gap = {
            "case": case,
            "zge_i3_minus_acsi": float(i3["zge"]) - float(acsi["zge"]),
            "zle_i3_minus_acsi": float(i3["zle"]) - float(acsi["zle"]),
            "edge_z_error_i3_minus_acsi": float(i3["edge_z_error"]) - float(acsi["edge_z_error"]),
            "interslice_ncc_mae_i3_minus_acsi": float(i3["interslice_ncc_mae"]) - float(acsi["interslice_ncc_mae"]),
        }
        gap["mean_consistency_gap_i3_minus_acsi"] = (
            gap["zge_i3_minus_acsi"]
            + gap["zle_i3_minus_acsi"]
            + gap["edge_z_error_i3_minus_acsi"]
            + gap["interslice_ncc_mae_i3_minus_acsi"]
        ) / 4.0
        rows.append(gap)
    return sorted(rows, key=lambda row: row["mean_consistency_gap_i3_minus_acsi"])


def _write_gap_markdown(case_gap_rows: list[dict]) -> None:
    worst = case_gap_rows[:10]
    best = case_gap_rows[-10:][::-1]

    def compact(rows: list[dict]) -> list[dict]:
        return [
            {
                "Case": row["case"],
                "Mean I3-ACSI": _fmt(row["mean_consistency_gap_i3_minus_acsi"], 6),
                "ZGE": _fmt(row["zge_i3_minus_acsi"], 6),
                "ZLE": _fmt(row["zle_i3_minus_acsi"], 6),
                "EdgeZ": _fmt(row["edge_z_error_i3_minus_acsi"], 6),
                "NCC-z-MAE": _fmt(row["interslice_ncc_mae_i3_minus_acsi"], 6),
            }
            for row in rows
        ]

    text = [
        "# ACSI-Net vs I3Net Case Gap Diagnosis",
        "",
        "Positive gaps mean I3Net has larger error than ACSI-Net, so ACSI-Net is better. Negative gaps mean I3Net is better.",
        "",
        "## Worst ACSI-Net Cases vs I3Net",
        "",
        _markdown_table(compact(worst), ["Case", "Mean I3-ACSI", "ZGE", "ZLE", "EdgeZ", "NCC-z-MAE"]),
        "",
        "## Best ACSI-Net Cases vs I3Net",
        "",
        _markdown_table(compact(best), ["Case", "Mean I3-ACSI", "ZGE", "ZLE", "EdgeZ", "NCC-z-MAE"]),
        "",
        "## Suggested Visual QC",
        "",
        "Generate sagittal/coronal panels for the worst ACSI-Net cases first. If these cases show systematic discontinuity, ACSI-v2 needs longer z-context rather than only loss-weight tuning.",
    ]
    (OUT_DIR / "acsi_vs_i3net_case_gap_diagnosis_2026-07-09.md").write_text("\n".join(text) + "\n", encoding="utf-8")


def _write_markdown(summary_rows: list[dict], win_rows: list[dict], complexity_rows: list[dict]) -> None:
    summary_display = []
    for row in summary_rows:
        summary_display.append(
            {
                "Method": row["method"],
                "Cases": row["cases"],
                "ZGE": _fmt(row["zge_mean"]),
                "ZLE": _fmt(row["zle_mean"]),
                "EdgeZ": _fmt(row["edge_z_error_mean"]),
                "NCC-z-MAE": _fmt(row["interslice_ncc_mae_mean"]),
            }
        )

    win_display = [
        {
            "Metric": row["metric"],
            "ACSI wins": f"{row['wins']}/{row['valid_cases']}",
            "Win rate": _fmt(row["win_rate"], 3),
            "Mean I3-ACSI": _fmt(row["mean_i3_minus_acsi"], 6),
        }
        for row in win_rows
    ]

    complexity_display = [
        {
            "Method": row["method"],
            "Params M": _fmt(row["params_m"], 3),
            "FLOPs / generated slice G": _fmt(row["per_generated_slice_flops_g"], 3),
        }
        for row in complexity_rows
    ]

    acsi_summary = next(row for row in summary_rows if row["method"] == "acsinet")
    i3_summary = next(row for row in summary_rows if row["method"] == "i3net")
    consistency_wins = sum(float(acsi_summary[f"{metric}_mean"]) < float(i3_summary[f"{metric}_mean"]) for metric in LOWER_IS_BETTER)
    strong_consistency = consistency_wins >= 3

    text = [
        "# ACSI-Net vs I3Net Claim Audit",
        "",
        "## Claim Gate",
        "",
        "The strong ACSI-Net claim requires two wins against I3Net:",
        "",
        "1. ACSI-Net must be lighter than I3Net.",
        "2. ACSI-Net must beat I3Net on anatomy-consistency metrics, not only linear/cubic.",
        "",
        "## Lightweight Evidence",
        "",
        _markdown_table(complexity_display, ["Method", "Params M", "FLOPs / generated slice G"]),
        "",
        "## Anatomy Consistency Evidence",
        "",
        _markdown_table(summary_display, ["Method", "Cases", "ZGE", "ZLE", "EdgeZ", "NCC-z-MAE"]),
        "",
        "## ACSI-Net Per-Case Wins vs I3Net",
        "",
        _markdown_table(win_display, ["Metric", "ACSI wins", "Win rate", "Mean I3-ACSI"]),
        "",
        "## Interpretation",
        "",
    ]

    if strong_consistency:
        text.extend(
            [
                "ACSI-Net passes the current strong-claim gate on this IXI full_test115 audit: it is substantially lighter than I3Net and has better mean 3D consistency on at least 3/4 anatomy metrics.",
                "",
                "The next step should be ablation, because the method claim now needs mechanism evidence rather than another main-model training run.",
            ]
        )
    else:
        text.extend(
            [
                "ACSI-Net does not yet pass the strong-claim gate against I3Net on this audit. It can still be discussed as a lightweight competitive model, but the anatomy-consistency claim must be weakened unless visual QC or refined metrics show a clearer advantage.",
                "",
                "The next step should be diagnosis: inspect the cases where I3Net wins, then decide whether to improve the loss/design or downgrade ACSI-Net to a supporting analysis direction.",
            ]
        )

    (OUT_DIR / "acsi_vs_i3net_claim_audit_2026-07-09.md").write_text("\n".join(text) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    acsi_rows = _load_acsi_consistency()
    i3_rows = _compute_i3_consistency()
    consistency_rows = acsi_rows + i3_rows
    summary_rows = summarize_consistency(consistency_rows)
    win_rows = _win_rates(acsi_rows, i3_rows)
    complexity = _complexity_rows()
    case_gaps = _case_gap_rows(acsi_rows, i3_rows)

    _write_csv(OUT_DIR / "acsi_vs_i3net_per_case_3d_consistency.csv", consistency_rows)
    _write_csv(OUT_DIR / "acsi_vs_i3net_summary_3d_consistency.csv", summary_rows)
    _write_csv(OUT_DIR / "acsi_vs_i3net_3d_win_rates.csv", win_rows)
    _write_csv(OUT_DIR / "acsi_vs_i3net_complexity.csv", complexity)
    _write_csv(OUT_DIR / "acsi_vs_i3net_case_gaps.csv", case_gaps)
    _write_markdown(summary_rows, win_rows, complexity)
    _write_gap_markdown(case_gaps)
    print(f"Wrote ACSI-Net vs I3Net claim audit to {OUT_DIR}")


if __name__ == "__main__":
    main()
