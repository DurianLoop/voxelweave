from __future__ import annotations

from pathlib import Path

from ixi_diffusion.common import ensure_dir, write_csv


ROOT = Path(__file__).resolve().parents[1]


def _dir_size(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(file.stat().st_size for file in path.rglob("*") if file.is_file())


def _count_files(path: Path, pattern: str = "*.nii.gz") -> int:
    if not path.exists():
        return 0
    return sum(1 for _ in path.rglob(pattern))


def _gb(size: int) -> float:
    return size / (1024**3)


def build_rows() -> list[dict]:
    configs = [
        {
            "profile": "full_test115",
            "dataset": "IXI",
            "source_dirs": [
                ROOT / "ixi_i3net" / "runs" / "full_test115_stable",
                ROOT / "ixi_hat_2p5d" / "runs" / "full_test115",
                ROOT / "ixi_swinir_2p5d" / "runs" / "full_test115",
                ROOT / "acsinet" / "runs" / "full_test115",
            ],
        },
        {
            "profile": "fastmri_full",
            "dataset": "fastMRI-brain T2",
            "source_dirs": [
                ROOT / "fastmri_brain_i3net" / "runs" / "full",
                ROOT / "fastmri_brain_hat_2p5d" / "runs" / "full",
                ROOT / "fastmri_brain_swinir_2p5d" / "runs" / "full",
            ],
        },
        {
            "profile": "ningxia_cv",
            "dataset": "NingXia T2 CV",
            "source_dirs": [
                ROOT / "ningxia_t2_i3net_cv" / "runs",
                ROOT / "ningxia_t2_hat_2p5d_cv" / "runs",
                ROOT / "ningxia_t2_swinir_2p5d_cv" / "runs",
            ],
        },
    ]
    rows = []
    for cfg in configs:
        run_metrics = ROOT / "rasinet" / "runs" / "posthoc_uncertainty" / cfg["profile"] / "metrics"
        report_dir = ROOT / "rasinet" / "reports" / "posthoc_uncertainty" / cfg["profile"]
        per_case = run_metrics / "per_case_posthoc_reliability.csv"
        cases = 0
        if per_case.exists():
            text = per_case.read_text(encoding="utf-8").splitlines()
            seen = set()
            header = text[0].split(",") if text else []
            if "case" in header:
                case_idx = header.index("case")
                for line in text[1:]:
                    if line.strip():
                        seen.add(line.split(",")[case_idx])
            cases = len(seen)
        source_size = sum(_dir_size(path) for path in cfg["source_dirs"])
        source_nii = sum(_count_files(path) for path in cfg["source_dirs"])
        rows.append(
            {
                "profile": cfg["profile"],
                "dataset": cfg["dataset"],
                "cases": cases,
                "source_dirs": len(cfg["source_dirs"]),
                "source_nii_files": source_nii,
                "source_size_gb": f"{_gb(source_size):.3f}",
                "posthoc_metrics_size_mb": f"{_dir_size(run_metrics) / (1024**2):.3f}",
                "report_size_mb": f"{_dir_size(report_dir) / (1024**2):.3f}",
                "training_needed": "no",
                "gpu_needed_for_posthoc": "no",
            }
        )
    return rows


def write_note(path: Path, rows: list[dict]) -> None:
    lines = [
        "# RASI post-hoc runtime / storage cost table",
        "",
        "本表记录当前 post-hoc reliability layer 的存储与执行成本属性。它只读取已有预测、GT 和 coarse interpolation，不重新训练模型。",
        "",
        "| Profile | Dataset | Cases | Source dirs | Source NIfTI files | Source size GB | Metrics MB | Reports MB | Training needed | GPU needed |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {profile} | {dataset} | {cases} | {source_dirs} | {source_nii_files} | {source_size_gb} | {posthoc_metrics_size_mb} | {report_size_mb} | {training_needed} | {gpu_needed_for_posthoc} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "说明：",
            "",
            "- `source_size_gb` 是已有 baseline/model output run directories 的总大小，不是本方法新增存储。",
            "- post-hoc 新增产物主要是 CSV、Markdown 和 PNG；相对已有 NIfTI 预测体积很小。",
            "- 若未来加入 TTA variance，GPU/额外推理成本需要单独列入，不应与当前 post-hoc disagreement 混为一谈。",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report_dir = ensure_dir(ROOT / "rasinet" / "reports" / "posthoc_uncertainty" / "paper_experiments")
    rows = build_rows()
    write_csv(report_dir / "runtime_storage_cost.csv", rows)
    write_note(report_dir / "runtime_storage_cost.md", rows)
    print(f"Wrote runtime/storage cost table to {report_dir}")


if __name__ == "__main__":
    main()
