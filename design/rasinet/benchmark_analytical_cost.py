from __future__ import annotations

import argparse
import csv
import json
import platform
import time
from pathlib import Path

import numpy as np
import yaml

from ixi_diffusion.common import ensure_dir, load_nifti
from topcow_diffusion.baselines import _upsample_z

from .committee_experiments import _baseline_path, _case_names, _folds, profile_sources


REPO_ROOT = Path(__file__).resolve().parents[2]


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _sparse_dir(run_dir: Path) -> Path:
    candidates = (run_dir / "eval_inputs" / "sparse", run_dir / "eval_sparse")
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError(f"sparse input directory not found under {run_dir}")


def run(config_path: Path) -> Path:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    output = ensure_dir(REPO_ROOT / config["output"])
    factor = int(config.get("factor", 4))
    case_limit = int(config.get("case_limit_per_profile", 10))
    rows: list[dict] = []

    for profile in config["profiles"]:
        sources = profile_sources(REPO_ROOT, profile)
        reference = sources[0]
        candidates: list[tuple[str | None, str]] = []
        for fold in _folds(sources):
            candidates.extend((fold, case) for case in _case_names(reference, fold))
        for fold, case in sorted(candidates, key=lambda item: ((item[0] or ""), item[1]))[:case_limit]:
            run_dir = reference.run_dir(fold)
            sparse_path = _sparse_dir(run_dir) / case
            start = time.perf_counter()
            sparse, _, _ = load_nifti(sparse_path)
            load_seconds = time.perf_counter() - start
            for kind in ("linear", "cubic"):
                start = time.perf_counter()
                reconstructed = _upsample_z(sparse, factor=factor, kind=kind)
                interpolation_seconds = time.perf_counter() - start
                expected_path = _baseline_path(reference, fold, kind, case)
                if not expected_path.is_file():
                    raise FileNotFoundError(expected_path)
                rows.append(
                    {
                        "profile": profile,
                        "fold": fold or "",
                        "case": case,
                        "kind": kind,
                        "input_shape": "x".join(str(value) for value in sparse.shape),
                        "output_shape": "x".join(str(value) for value in reconstructed.shape),
                        "load_seconds": load_seconds,
                        "interpolation_seconds": interpolation_seconds,
                        "saved_output_bytes": expected_path.stat().st_size,
                        "finite": int(np.isfinite(reconstructed).all()),
                    }
                )

    _write_csv(output / "per_case.csv", rows)
    summary: list[dict] = []
    for (profile, kind), group in _groups(rows).items():
        times = np.asarray([float(row["interpolation_seconds"]) for row in group])
        sizes = np.asarray([int(row["saved_output_bytes"]) for row in group])
        summary.append(
            {
                "profile": profile,
                "kind": kind,
                "number_of_cases": len(group),
                "seconds_mean": float(np.mean(times)),
                "seconds_p95": float(np.percentile(times, 95.0)),
                "saved_output_mib_mean": float(np.mean(sizes) / (1024**2)),
            }
        )
    _write_csv(output / "summary.csv", summary)
    (output / "environment.json").write_text(
        json.dumps(
            {
                "python": platform.python_version(),
                "platform": platform.platform(),
                "processor": platform.processor(),
                "device": "CPU",
                "factor": factor,
                "case_limit_per_profile": case_limit,
                "timing_scope": "interpolation only; NIfTI load and save excluded",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return output


def _groups(rows: list[dict]) -> dict[tuple[str, str], list[dict]]:
    grouped: dict[tuple[str, str], list[dict]] = {}
    for row in rows:
        grouped.setdefault((str(row["profile"]), str(row["kind"])), []).append(row)
    return grouped


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark analytical x4 interpolation without rewriting outputs.")
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    path = args.config if args.config.is_absolute() else REPO_ROOT / args.config
    print(run(path.resolve()))


if __name__ == "__main__":
    main()
