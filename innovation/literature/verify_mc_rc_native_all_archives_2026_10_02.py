"""Refresh README-dependent static manifests and record real write/read-only checks."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "SESSION_ARCHIVE_VERIFICATION_MC_RC_NATIVE_2026-10-02.json"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    prior_record = None
    if OUT.exists():
        attempt = len(list(ROOT.glob("SESSION_ARCHIVE_VERIFICATION_MC_RC_NATIVE_2026-10-02_attempt_*.json"))) + 1
        prior_record = OUT.with_name(OUT.stem + f"_attempt_{attempt:02d}.json")
        prior_record.write_bytes(OUT.read_bytes())
    result = {
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "scope": "static archive checks only; keeps original label/crosswalk failures and live queue",
        "status": "checks_in_progress", "all_checks_passed": False,
        "prior_record": prior_record.name if prior_record else None,
        "scientific_goal_complete": False, "records": [],
    }
    # Publish this linked record before checking Markdown existence.
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    scripts = [
        "literature/verify_author_ensure_mslesseg_stage_archive.py",
        "literature/verify_task_throughplane_stage_archive.py",
        "literature/verify_risk_action_stage_archive.py",
        "literature/verify_local_action_and_operator_archive.py",
        "literature/verify_action_crossmoda_stage_archive.py",
        "literature/verify_mc_rc_native_stage_archive.py",
        "verify_archive.py",
    ]
    if "--current-only" in sys.argv:
        # The action stage also includes the newly added MC_RC documents.
        scripts = scripts[-3:]
    for script in scripts:
        for write in (True, False):
            command = [sys.executable, "-B", str(ROOT / script)] + (["--write"] if write else [])
            started = datetime.now(timezone.utc).isoformat()
            run = subprocess.run(command, cwd=ROOT.parent, capture_output=True, timeout=180)
            stdout = run.stdout.decode("utf-8", errors="replace")
            stderr = run.stderr.decode("utf-8", errors="replace")
            try:
                parsed = json.loads(stdout)
            except json.JSONDecodeError:
                parsed = None
            result["records"].append({
                "script": script, "command": command, "write": write,
                "started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(),
                "returncode": run.returncode, "stdout": stdout, "stderr": stderr, "parsed": parsed,
            })
            OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(json.dumps({
                "script": script, "write": write, "returncode": run.returncode,
                "errors": parsed.get("errors") if isinstance(parsed, dict) else "unparsed",
                "summary": {k: parsed[k] for k in ("pdfs", "evidence_files", "local_links_checked", "files") if isinstance(parsed, dict) and k in parsed},
            }, ensure_ascii=False), flush=True)
            if run.returncode:
                result["status"] = "failed"
                OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                return run.returncode
    result.update(status="complete", all_checks_passed=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
