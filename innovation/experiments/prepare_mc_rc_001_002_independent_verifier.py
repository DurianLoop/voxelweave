"""Materialize exact, recorded adaptations of the frozen independent numerical verifier."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments/verify_mc_rc_three_development_action_oracle.py"
TARGET = ROOT / "experiments/verify_mc_rc_001_002_raw_action_oracle.py"
OUT = ROOT / "experiments/mc_rc_001_002_raw_action_oracle/independent_verifier_source_adaptation.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    text = SOURCE.read_text(encoding="utf-8")
    replacements = [
        ('OUT = ROOT / "experiments/mc_rc_three_development_action_oracle"', 'OUT = ROOT / "experiments/mc_rc_001_002_raw_action_oracle"'),
        ('"literature/source_cache/mc_rc_004_006_native_headers_2026-10-02"', '"literature/source_cache/mc_rc_three_patient_headers_2026-10-02"'),
        ('len(result["patients"]) != 3', 'len(result["patients"]) != 2'),
        ('if a["base"] == "pipeline_pchip")["development_gate_passed"] for p in result["patients"])', 'if a["base"] == "raw_pchip")["development_gate_passed"] for p in result["patients"])'),
        ('"Cannot verify an incomplete fixed-three development experiment"', '"Cannot verify an incomplete fixed-two development experiment"'),
    ]
    applied = []
    for before, after in replacements:
        occurrences = text.count(before)
        if occurrences != 1:
            raise ValueError("Expected unique frozen source replacement: " + before)
        text = text.replace(before, after)
        applied.append({"before": before, "after": after, "occurrences": occurrences})
    compile(text, str(TARGET), "exec")
    with TARGET.open("x", encoding="utf-8") as f:
        f.write(text)
    record = {"script_sha256": sha(__file__), "source_file": SOURCE.relative_to(ROOT).as_posix(), "source_sha256": sha(SOURCE),
              "target_file": TARGET.relative_to(ROOT).as_posix(), "target_sha256": sha(TARGET), "replacements": applied,
              "scope": "count/path/raw-primary adaptations only; original independent Hermite/vectorized/direct-forward algorithms retained",
              "plan_sha256": sha(ROOT / "MC_RC_001_002_RAW_ACTION_EXECUTION_PLAN_2026-10-02.md")}
    OUT.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"complete": True, "replacements": len(applied), "target_file": record["target_file"]}))


if __name__ == "__main__":
    main()
