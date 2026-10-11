"""Capture progress only, following a real session83910 live poll."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    folder = ROOT / "experiments/vs_seg_full_volume_queue"
    status = json.loads((ROOT / "experiments/vs_seg_full_volume_cohort/status.json").read_text(encoding="utf-8"))
    driver = json.loads((folder / "attempt_01.json").read_text(encoding="utf-8"))
    result = {"observed_utc": datetime.now(timezone.utc).isoformat(), "unified_exec_session": 83910,
              "poll_returned_live": True, "poll_evidence": "actual write_stdin returned session_id83910 in this continuation",
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "contract_sha256": hashlib.sha256((ROOT / "experiments/vs_seg_full_volume_cohort/run_contract.json").read_bytes()).hexdigest(),
              "driver_complete": driver["complete"], "active_stage": driver["active_stage"],
              "complete_main_patients": status["complete_main_patients"], "fixed_main_denominator": status["fixed_main_denominator"],
              "completed_conditions": status["completed_conditions"], "main_complete": status["main_complete"],
              "historical_log_tail": (folder / "inference_attempt_01.log").read_text(encoding="utf-8", errors="replace").splitlines()[-8:],
              "scope": "separately read progress/log snapshot; no subcohort performance analysis or inference change",
              "scientific_goal_complete": False, "dynamic_subcohort_statistics_computed": False}
    out = ROOT / "literature/source_cache/mc_rc_action_batch_queue_observation_2026-10-02.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("observed_utc", "complete_main_patients", "fixed_main_denominator", "completed_conditions", "active_stage")}))


if __name__ == "__main__":
    main()
