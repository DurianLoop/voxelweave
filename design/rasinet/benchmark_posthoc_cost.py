from __future__ import annotations

import argparse
import csv
import ctypes
import json
import platform
import os
import time
from pathlib import Path

import nibabel as nib
import numpy as np
import yaml

from .committee_experiments import _baseline_path, _case_names, _folds, _prediction_path, profile_sources
from .icassp_scores import deployment_mask, generated_indices, score_map


REPO_ROOT = Path(__file__).resolve().parents[2]


def _rss_bytes() -> int:
    """Return the current resident working set without a third-party dependency."""
    if os.name == "nt":
        class ProcessMemoryCounters(ctypes.Structure):
            _fields_ = [
                ("cb", ctypes.c_ulong),
                ("PageFaultCount", ctypes.c_ulong),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        counters = ProcessMemoryCounters()
        counters.cb = ctypes.sizeof(counters)
        get_current_process = ctypes.windll.kernel32.GetCurrentProcess
        get_current_process.restype = ctypes.c_void_p
        get_process_memory_info = ctypes.windll.psapi.GetProcessMemoryInfo
        get_process_memory_info.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ProcessMemoryCounters),
            ctypes.c_ulong,
        ]
        get_process_memory_info.restype = ctypes.c_int
        handle = get_current_process()
        if not get_process_memory_info(
            handle, ctypes.byref(counters), counters.cb
        ):
            raise OSError("GetProcessMemoryInfo failed")
        return int(counters.WorkingSetSize)
    import resource

    usage = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return usage if platform.system() == "Darwin" else usage * 1024


def _load(path: Path) -> np.ndarray:
    array = nib.load(str(path)).get_fdata(dtype=np.float32)
    if array.ndim != 3 or not np.isfinite(array).all():
        raise ValueError(f"invalid volume: {path}")
    return array


def _write(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run(config_path: Path) -> Path:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    factor = int(config.get("factor", 4))
    target = str(config.get("target", "swinir"))
    case_limit = int(config.get("case_limit_per_profile", 10))
    output = REPO_ROOT / str(config["output"])
    rows: list[dict] = []
    for profile in config["profiles"]:
        sources = profile_sources(REPO_ROOT, profile)
        reference = sources[0]
        target_source = next(source for source in sources if source.name == target)
        candidates: list[tuple[str | None, str]] = []
        for fold in _folds(sources):
            candidates.extend((fold, case) for case in _case_names(reference, fold))
        for fold, case in sorted(candidates, key=lambda item: ((item[0] or ""), item[1]))[:case_limit]:
            paths = {
                source.name: _prediction_path(source, fold, case)
                for source in sources
            }
            paths["linear"] = _baseline_path(reference, fold, "linear", case)
            paths["cubic"] = _baseline_path(reference, fold, "cubic", case)
            total_start = time.perf_counter()
            load_start = time.perf_counter()
            volumes = {name: _load(path) for name, path in paths.items()}
            load_seconds = time.perf_counter() - load_start
            rss_after_load = _rss_bytes()
            committee = {name: volume for name, volume in volumes.items() if name != target}
            if target in committee:
                raise AssertionError("target leaked into post-hoc benchmark committee")
            score_start = time.perf_counter()
            indices = list(generated_indices(volumes[target].shape[2], factor))
            score = score_map(target, volumes[target], committee, "target_abs_median")[:, :, indices]
            mask = deployment_mask(volumes[target], committee, "target_0.01", factor)[:, :, indices]
            examination_score = float(np.mean(score[mask]))
            score_seconds = time.perf_counter() - score_start
            rss_after_score = _rss_bytes()
            total_seconds = time.perf_counter() - total_start
            rows.append(
                {
                    "profile": profile,
                    "fold": fold or "",
                    "case": case,
                    "target": target,
                    "committee": ";".join(committee),
                    "source_files": len(paths),
                    "source_bytes": sum(path.stat().st_size for path in paths.values()),
                    "load_seconds": load_seconds,
                    "score_seconds": score_seconds,
                    "total_seconds": total_seconds,
                    "rss_after_load_bytes": rss_after_load,
                    "rss_after_score_bytes": rss_after_score,
                    "observed_peak_rss_bytes": max(rss_after_load, rss_after_score),
                    "examination_score": examination_score,
                }
            )
    output.mkdir(parents=True, exist_ok=True)
    _write(output / "per_case.csv", rows)
    summary: list[dict] = []
    for profile in [*config["profiles"], "all"]:
        selected = rows if profile == "all" else [row for row in rows if row["profile"] == profile]
        result: dict[str, object] = {"profile": profile, "number_of_cases": len(selected)}
        for metric in ("load_seconds", "score_seconds", "total_seconds"):
            values = np.asarray([float(row[metric]) for row in selected])
            result[f"{metric}_mean"] = float(np.mean(values))
            result[f"{metric}_p95"] = float(np.percentile(values, 95.0))
        result["source_mib_mean"] = float(np.mean([int(row["source_bytes"]) for row in selected]) / (1024**2))
        result["observed_peak_rss_gib"] = float(max(int(row["observed_peak_rss_bytes"]) for row in selected) / (1024**3))
        summary.append(result)
    _write(output / "summary.csv", summary)
    (output / "environment.json").write_text(
        json.dumps(
            {
                "python": platform.python_version(),
                "platform": platform.platform(),
                "processor": platform.processor(),
                "device": "CPU",
                "target": target,
                "ground_truth_read": False,
                "timing_scope": "NIfTI prediction I/O plus default score and deployment mask",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark a ground-truth-free stored-output reliability audit.")
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    path = args.config if args.config.is_absolute() else REPO_ROOT / args.config
    print(run(path.resolve()))


if __name__ == "__main__":
    main()
