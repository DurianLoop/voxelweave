from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Literal


Stage = Literal["static", "profile", "smoke", "mini"]
PIPELINE_STAGES = ["static", "preflight", "profile", "smoke", "mini"]


def _number(value: str) -> float:
    match = re.search(r"[-+]?\d+(?:\.\d+)?", value)
    return float(match.group(0)) if match else float("nan")


def parse_nvidia_smi_snapshot(gpu_line: str, process_lines: str) -> dict[str, object]:
    gpu_parts = [part.strip() for part in gpu_line.strip().split(",")]
    if len(gpu_parts) < 4:
        raise ValueError(f"Unexpected nvidia-smi GPU row: {gpu_line!r}")
    processes: list[dict[str, object]] = []
    for line in process_lines.splitlines():
        if not line.strip():
            continue
        parts = [part.strip() for part in line.split(",")]
        if len(parts) < 2:
            continue
        used_memory = _number(parts[1])
        processes.append(
            {
                "pid": int(_number(parts[0])),
                "used_memory_mib": used_memory if not math.isnan(used_memory) else None,
            }
        )
    return {
        "gpu_name": gpu_parts[0],
        "memory_total_mib": _number(gpu_parts[1]),
        "memory_used_mib": _number(gpu_parts[2]),
        "gpu_utilization_percent": _number(gpu_parts[3]),
        "compute_processes": processes,
    }


def stage_sequence(through: Stage) -> list[str]:
    end = PIPELINE_STAGES.index(through)
    return PIPELINE_STAGES[: end + 1]


PACKAGE_DIR = Path(__file__).resolve().parent
REPORT_ROOT = PACKAGE_DIR / "reports" / "efficiency"
STATE_PATH = REPORT_ROOT / "one_click_state.json"


def _now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _load_state() -> dict[str, object]:
    if not STATE_PATH.exists():
        return {"created_at": _now(), "stages": {}}
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def _save_state(state: dict[str, object]) -> None:
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = _now()
    STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def _mark(state: dict[str, object], stage: str, status: str, **details: object) -> None:
    stages = state.setdefault("stages", {})
    assert isinstance(stages, dict)
    stages[stage] = {"status": status, "updated_at": _now(), **details}
    _save_state(state)


def _query_gpu_snapshot() -> dict[str, object]:
    gpu = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=name,memory.total,memory.used,utilization.gpu",
            "--format=csv,noheader,nounits",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    processes = subprocess.run(
        ["nvidia-smi", "--query-compute-apps=pid,used_memory", "--format=csv,noheader,nounits"],
        check=True,
        capture_output=True,
        text=True,
    )
    gpu_line = next(line for line in gpu.stdout.splitlines() if line.strip())
    return parse_nvidia_smi_snapshot(gpu_line, processes.stdout)


def _run_child(module: str, profile: str) -> None:
    command = [sys.executable, "-u", "-B", "-m", module, "--profile", profile]
    print("Running:", subprocess.list2cmdline(command), flush=True)
    subprocess.run(command, check=True, env=os.environ.copy())


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _run_acceptance(profile_name: str, component_result: dict[str, object], require_quality: bool) -> dict[str, object]:
    from .acceptance import evaluate_quality_gate
    from .settings import build_paths

    paths = build_paths(profile_name)
    required = [
        paths.run_dir / "run_manifest.json",
        paths.run_dir / "training_history.csv",
        paths.run_dir / "training_history.json",
        paths.checkpoints / "ecsinet_epoch_best.pth",
        paths.checkpoints / "ecsinet_epoch_final.pth",
        paths.metrics / "summary_metrics.csv",
        paths.metrics / "per_case_metrics.csv",
        paths.metrics / "paper_table.csv",
        paths.metrics / "complexity.json",
        paths.metrics / "mask_statistics.csv",
        paths.metrics / "residual_statistics.csv",
        paths.metrics / "mask_correlation.csv",
    ]
    failed = [f"missing artifact: {path}" for path in required if not path.is_file()]
    history_rows = _read_csv(paths.run_dir / "training_history.csv") if (paths.run_dir / "training_history.csv").is_file() else []
    if not history_rows:
        failed.append("training history is empty")
    elif any(int(float(row.get("skipped_nonfinite", "0") or 0)) != 0 for row in history_rows):
        failed.append("skipped_nonfinite == 0")
    summary_rows = _read_csv(paths.metrics / "summary_metrics.csv") if (paths.metrics / "summary_metrics.csv").is_file() else []
    methods = {row.get("method", "") for row in summary_rows}
    if not {"ecsinet", "linear", "cubic"}.issubset(methods):
        failed.append("summary contains ecsinet, linear, and cubic")
    quality = evaluate_quality_gate(summary_rows) if require_quality and summary_rows else {"passed": True, "failed_checks": []}
    if require_quality and not bool(quality["passed"]):
        failed.extend([f"quality gate: {item}" for item in quality["failed_checks"]])
    if not bool(component_result["passed"]):
        failed.extend([f"component gate: {item}" for item in component_result["gate"]["failed_checks"]])
    expected_cases = len(json.loads((paths.run_dir / "run_manifest.json").read_text(encoding="utf-8"))["eval_cases"]) if (paths.run_dir / "run_manifest.json").is_file() else 0
    generated_cases = len(list(paths.model_outputs.glob("*.nii.gz")))
    if expected_cases != generated_cases:
        failed.append(f"generated case count {generated_cases} == manifest case count {expected_cases}")
    result = {
        "passed": not failed,
        "profile": profile_name,
        "required_artifacts": [str(path) for path in required],
        "failed_checks": failed,
        "quality_gate": quality,
        "component_gate": component_result,
        "expected_cases": expected_cases,
        "generated_cases": generated_cases,
    }
    report_dir = REPORT_ROOT / profile_name
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "stage_acceptance.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [
        f"# ECSI-Net {profile_name} Stage Acceptance",
        "",
        f"Overall: `{'PASS' if result['passed'] else 'FAIL'}`",
        "",
        f"Generated cases: `{generated_cases}/{expected_cases}`",
        "",
        "Failed checks:",
    ]
    lines.extend([f"- {item}" for item in failed] or ["- None"])
    (report_dir / "stage_acceptance.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result


def _profile_stage() -> dict[str, object]:
    import torch

    from .efficiency import run_ecsinet_profile

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for acceptance profiling")
    output_dir = PACKAGE_DIR / "runs" / "profile"
    result = run_ecsinet_profile(
        output_dir=output_dir,
        device=torch.device("cuda"),
        configurations=[
            {"name": "ECSI-Tiny", "channels": 32, "num_blocks": 6, "batch_sizes": [16, 32, 64]},
            {"name": "ECSI-Base", "channels": 48, "num_blocks": 8, "batch_sizes": [8, 16, 32]},
        ],
        image_size=256,
        warmup=20,
        inference_iterations=100,
        training_iterations=20,
    )
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    (REPORT_ROOT / "profile_summary.md").write_text(
        (output_dir / "profile_summary.md").read_text(encoding="utf-8"), encoding="utf-8"
    )
    return {**result, "output_dir": str(output_dir)}


def _model_stage(profile_name: str, max_samples: int, visual_count: int, require_quality: bool) -> dict[str, object]:
    from .acceptance import analyze_checkpoint
    from .settings import build_paths

    _run_child("ixi_ecsinet_2p5d.run_all", profile_name)
    _run_child("ixi_ecsinet_2p5d.paper_table", profile_name)
    paths = build_paths(profile_name)
    report_dir = REPORT_ROOT / profile_name
    component = analyze_checkpoint(
        checkpoint=paths.checkpoints / "ecsinet_epoch_best.pth",
        profile_name=profile_name,
        metrics_dir=paths.metrics,
        report_dir=report_dir,
        max_samples=max_samples,
        visual_count=visual_count,
    )
    return _run_acceptance(profile_name, component, require_quality=require_quality)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run ECSI-Net acceptance stages with automatic gates.")
    parser.add_argument("--through", choices=["static", "profile", "smoke", "mini"], default="mini")
    parser.add_argument("--restart", action="store_true", help="Ignore prior pass state and rerun completed GPU stages.")
    args = parser.parse_args()

    from .acceptance import gpu_preflight, run_static_validation

    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    state = {"created_at": _now(), "stages": {}} if args.restart else _load_state()
    state["requested_through"] = args.through
    _save_state(state)
    stages = stage_sequence(args.through)

    print("[1] Static validation", flush=True)
    static = run_static_validation(REPORT_ROOT)
    _mark(state, "static", "passed" if static["passed"] else "failed", report=str(REPORT_ROOT / "static_validation.md"))
    if not bool(static["passed"]):
        return 1
    if "preflight" not in stages:
        return 0

    print("[2] GPU preflight", flush=True)
    snapshot = _query_gpu_snapshot()
    preflight = gpu_preflight(snapshot, own_pid=os.getpid())
    (REPORT_ROOT / "gpu_preflight.json").write_text(json.dumps(preflight, indent=2), encoding="utf-8")
    if not bool(preflight["passed"]):
        _mark(state, "preflight", "blocked", reasons=preflight["reasons"], snapshot=snapshot)
        print(f"GPU preflight blocked: {', '.join(preflight['reasons'])}", flush=True)
        return 2
    _mark(state, "preflight", "passed", snapshot=snapshot)

    prior_stages = state.get("stages", {})
    assert isinstance(prior_stages, dict)
    try:
        if "profile" in stages:
            profile_state = prior_stages.get("profile", {})
            if args.restart or not isinstance(profile_state, dict) or profile_state.get("status") != "passed":
                print("[3] Synthetic efficiency profile", flush=True)
                profile_result = _profile_stage()
                _mark(state, "profile", "passed", **profile_result)
            else:
                print("[3] Synthetic efficiency profile: already passed, resuming", flush=True)
        if "smoke" in stages:
            smoke_state = prior_stages.get("smoke", {})
            if args.restart or not isinstance(smoke_state, dict) or smoke_state.get("status") != "passed":
                print("[4] Smoke", flush=True)
                smoke = _model_stage("smoke", max_samples=256, visual_count=3, require_quality=False)
                _mark(state, "smoke", "passed" if smoke["passed"] else "blocked", report=str(REPORT_ROOT / "smoke" / "stage_acceptance.md"))
                if not bool(smoke["passed"]):
                    return 3
            else:
                print("[4] Smoke: already passed, resuming", flush=True)
        if "mini" in stages:
            mini_state = prior_stages.get("mini", {})
            if args.restart or not isinstance(mini_state, dict) or mini_state.get("status") != "passed":
                print("[5] Mini", flush=True)
                mini = _model_stage("mini", max_samples=512, visual_count=5, require_quality=True)
                _mark(state, "mini", "passed" if mini["passed"] else "blocked", report=str(REPORT_ROOT / "mini" / "stage_acceptance.md"))
                if not bool(mini["passed"]):
                    return 4
            else:
                print("[5] Mini: already passed, resuming", flush=True)
    except Exception as exc:
        active = next((stage for stage in reversed(stages) if stage not in {"static", "preflight"}), "pipeline")
        _mark(state, active, "failed", error=repr(exc))
        raise

    state["result"] = "mini_passed_full_blocked_at_B8_pending_pareto_baselines" if args.through == "mini" else "requested_stages_passed"
    _save_state(state)
    print("Requested ECSI-Net stages passed.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
