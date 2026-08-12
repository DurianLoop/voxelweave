from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .settings import PROFILES, build_paths


METHOD_LABELS = {
    "linear": "Linear",
    "cubic": "Cubic",
    "resunet": "ResUNet residual",
    "saint": "SAINT-style",
    "diffusion": "HiFiDiff residual",
}

METHOD_ORDER = ["linear", "cubic", "resunet", "saint", "diffusion"]

MAIN_METRICS = ["PSNR", "SSIM", "MAE", "MSE", "NCC"]


def _read_profile(profile_name: str) -> pd.DataFrame:
    paths = build_paths(profile_name)
    profile = PROFILES[profile_name]
    summary_path = paths.metrics / "summary_metrics.csv"
    if not summary_path.exists():
        return pd.DataFrame()
    summary = pd.read_csv(summary_path)
    ext_path = paths.metrics / "extended_summary_metrics.csv"
    if ext_path.exists():
        ext = pd.read_csv(ext_path)
        summary = summary.merge(ext, on="method", how="left", suffixes=("", "_ext"))
    rows = []
    for _, row in summary.iterrows():
        rows.append(
            {
                "Dataset": "IXI",
                "Modality": profile.modality,
                "Scale": f"x{profile.stride}",
                "Direction": "z / through-plane",
                "Profile": profile_name,
                "Method": row["method"],
                "Cases": int(row["cases"]),
                "PSNR": float(row["psnr_mean"]),
                "SSIM": float(row["ssim_mean"]),
                "SSIMa": row.get("ssim_a_mean", ""),
                "SSIMc": row.get("ssim_c_mean", ""),
                "SSIMs": row.get("ssim_s_mean", ""),
                "MAE": float(row["mae_mean"]),
                "MSE": float(row["mse_mean"]),
                "RMSE": row.get("rmse_mean", float(row["mse_mean"]) ** 0.5),
                "NMSE": row.get("nmse_mean", ""),
                "NRMSE": row.get("nrmse_mean", ""),
                "NCC": float(row["ncc_mean"]),
                "SNLI": row.get("snli_mean", ""),
                "Gradient-MAE": row.get("gradient_mae_mean", ""),
                "LPIPS": row.get("lpips_mean", ""),
                "Metric seconds/case": row.get("metric_seconds_per_case", row.get("seconds_per_case", "")),
                "Source": "ours rerun" if row["method"] in {"linear", "cubic", "saint"} else "ours internal baseline",
            }
        )
    return pd.DataFrame(rows)


def _dataset_label(row: pd.Series) -> str:
    return f"{row['Dataset']}-{row['Modality']} {row['Scale']} (n={int(row['Cases'])})"


def _format_value(value: object) -> str:
    if value == "" or pd.isna(value):
        return ""
    return f"{float(value):.4f}"


def _format_wide_markdown(df: pd.DataFrame) -> str:
    table = df.copy()
    table["DatasetLabel"] = table.apply(_dataset_label, axis=1)
    dataset_labels = list(dict.fromkeys(table["DatasetLabel"].tolist()))
    methods = [method for method in METHOD_ORDER if method in set(table["Method"])]
    methods += sorted(set(table["Method"]) - set(methods))

    compact_columns = ["Method", "Scale", *dataset_labels]
    compact_lines = [
        "| " + " | ".join(compact_columns) + " |",
        "| " + " | ".join(["---"] * len(compact_columns)) + " |",
    ]
    for method in methods:
        method_rows = table[table["Method"] == method]
        scale = "/".join(sorted(set(str(item) for item in method_rows["Scale"])))
        out = {
            "Method": METHOD_LABELS.get(method, str(method)),
            "Scale": scale,
        }
        for label in dataset_labels:
            selected = method_rows[method_rows["DatasetLabel"] == label]
            if selected.empty:
                out[label] = ""
                continue
            row = selected.iloc[0]
            out[label] = "<br>".join(f"{metric}: {_format_value(row[metric])}" for metric in MAIN_METRICS)
        compact_lines.append("| " + " | ".join(str(out.get(col, "")) for col in compact_columns) + " |")

    columns = ["Method", "Scale"]
    for label in dataset_labels:
        for metric in MAIN_METRICS:
            columns.append(f"{label} {metric}")

    lines = [
        "# Unified Experiment Master Table",
        "",
        "主表采用论文式横向布局：`Method` 放在最左侧，数据集/模态横向展开。这里默认只展示非派生主指标：`PSNR / SSIM / MAE / MSE / NCC`。",
        "",
        "完整归档 CSV 仍保留全部指标，包含 `SSIMa/c/s`、`RMSE`、`NMSE`、`NRMSE`、`SNLI`、`Gradient-MAE`、`LPIPS` 等，等某个实验整体表现稳定后再补进最终论文表。",
        "",
        "## Compact Main Table",
        "",
        "每个数据集单元格内顺序为 `PSNR / SSIM / MAE / MSE / NCC`。",
        "",
        "\n".join(compact_lines),
        "",
        "## Expanded Main Table",
        "",
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for method in methods:
        method_rows = table[table["Method"] == method]
        scale = "/".join(sorted(set(str(item) for item in method_rows["Scale"])))
        out = {
            "Method": METHOD_LABELS.get(method, str(method)),
            "Scale": scale,
        }
        for label in dataset_labels:
            selected = method_rows[method_rows["DatasetLabel"] == label]
            for metric in MAIN_METRICS:
                key = f"{label} {metric}"
                out[key] = "" if selected.empty else _format_value(selected.iloc[0][metric])
        lines.append("| " + " | ".join(str(out.get(col, "")) for col in columns) + " |")
    return "\n".join(lines)


def _format_markdown(df: pd.DataFrame) -> str:
    display = df.copy()
    for col in [
        "PSNR",
        "SSIM",
        "SSIMa",
        "SSIMc",
        "SSIMs",
        "MAE",
        "MSE",
        "RMSE",
        "NMSE",
        "NRMSE",
        "NCC",
        "SNLI",
        "Gradient-MAE",
        "LPIPS",
        "Metric seconds/case",
    ]:
        if col in display:
            display[col] = display[col].map(lambda x: "" if pd.isna(x) or x == "" else f"{float(x):.4f}")
    header = list(display.columns)
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * len(header)) + " |",
    ]
    for _, row in display.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in header) + " |")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profiles", nargs="+", default=["resunet_full_t1", "resunet_full_t2", "resunet_full"])
    parser.add_argument("--out", type=Path, default=Path("docx") / "experiment" / "experiment_master_table")
    args = parser.parse_args()

    frames = [_read_profile(profile) for profile in args.profiles]
    table = pd.concat([frame for frame in frames if not frame.empty], ignore_index=True)
    if table.empty:
        raise FileNotFoundError("No summary_metrics.csv found for requested profiles")
    csv_path = args.out.with_suffix(".csv")
    md_path = args.out.with_suffix(".md")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(csv_path, index=False)
    md_path.write_text(_format_wide_markdown(table) + "\n", encoding="utf-8")
    detail_path = args.out.with_name(args.out.name + "_long").with_suffix(".md")
    detail_path.write_text("# Unified Experiment Master Table Long Form\n\n" + _format_markdown(table) + "\n", encoding="utf-8")
    print(f"Wrote {csv_path}")
    print(f"Wrote {md_path}")
    print(f"Wrote {detail_path}")


if __name__ == "__main__":
    main()
