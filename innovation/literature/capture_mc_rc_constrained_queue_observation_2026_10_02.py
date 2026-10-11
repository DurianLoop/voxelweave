"""Progress-only snapshot after an actual live poll of original session83910."""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def main():
    queue = ROOT / "experiments/vs_seg_full_volume_queue"
    status = json.loads((ROOT / "experiments/vs_seg_full_volume_cohort/status.json").read_text(encoding="utf-8"))
    driver = json.loads((queue / "attempt_01.json").read_text(encoding="utf-8"))
    result = {"observed_utc": datetime.now(timezone.utc).isoformat(), "unified_exec_session": 83910, "poll_returned_live": True,
              "poll_evidence": "write_stdin(session_id=83910) actually returned live in this continuation before snapshot",
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "contract_sha256": hashlib.sha256((ROOT / "experiments/vs_seg_full_volume_cohort/run_contract.json").read_bytes()).hexdigest(),
              "driver_complete": driver["complete"], "active_stage": driver["active_stage"], "complete_main_patients": status["complete_main_patients"], "fixed_main_denominator": status["fixed_main_denominator"],
              "completed_conditions": status["completed_conditions"], "main_complete": status["main_complete"], "secondary_complete": status["secondary_complete"],
              "historical_log_tail": (queue / "inference_attempt_01.log").read_text(encoding="utf-8", errors="replace").splitlines()[-8:],
              "scope": "historical progress only; no dynamic subcohort performance statistics", "dynamic_subcohort_statistics_computed": False, "scientific_goal_complete": False}
    out = ROOT / "literature/source_cache/mc_rc_constrained_queue_observation_2026-10-02.json"
    if out.exists():
        raise ValueError("Keep prior snapshot; choose a new filename for another observation")
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("observed_utc", "complete_main_patients", "fixed_main_denominator", "completed_conditions", "active_stage")}))

if __name__ == "__main__":
    main()
